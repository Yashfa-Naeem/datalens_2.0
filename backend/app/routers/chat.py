"""Natural-language Q&A over uploaded data using Groq with tool calling."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Literal

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from groq import Groq
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import engine, get_db
from .data import _get_dataset_or_404
from .upload import ANALYSIS_ROW_CAP, load_dataset_table_sample

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_TOOL_ROUNDS = 10
MAX_PREVIEW_ROWS = 100
SQL_RESULT_CAP = 1000

FORBIDDEN_SQL = re.compile(
    r"\b(insert|update|delete|drop|attach|detach|pragma|create|alter|truncate|"
    r"replace|merge|vacuum|analyze|reindex|grant|revoke)\b",
    re.IGNORECASE,
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    dataset_id: int = Field(..., ge=1)
    message: str = Field(..., min_length=1, max_length=8000)
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=24,
        description="Optional prior turns (user/assistant) for context.",
    )


class ChatResponse(BaseModel):
    answer: str
    dataset_id: int
    model: str


def _require_groq_client() -> Groq:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not set. Add it to your environment to use /api/chat.",
        )
    return Groq(api_key=key)


def _validate_select_sql(sql: str, allowed_table: str) -> str:
    s = sql.strip().rstrip(";")
    if not s:
        raise ValueError("Empty SQL query.")
    if ";" in s:
        raise ValueError("Multiple SQL statements are not allowed.")
    if "--" in s or "/*" in s:
        raise ValueError("SQL comments are not allowed.")
    if not s.lower().startswith("select"):
        raise ValueError("Only SELECT queries are supported.")
    if FORBIDDEN_SQL.search(s):
        raise ValueError("Query contains forbidden SQL keywords.")
    low = s.lower()
    blocked = ("sqlite_master", "sqlite_schema", "sqlite_temp")
    for b in blocked:
        if b in low:
            raise ValueError(f"Access to {b} is not allowed.")
    if allowed_table not in s and f'"{allowed_table}"' not in s:
        raise ValueError(
            f"The query must reference this dataset's table: {allowed_table!r}.",
        )
    if not re.search(r"\blimit\s+\d+", s, re.IGNORECASE):
        s = f"{s} LIMIT {SQL_RESULT_CAP}"
    return s


def _rows_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = df.replace({np.nan: None}).head(SQL_RESULT_CAP).to_dict(orient="records")
    return records  # type: ignore[return-value]


def _tool_query_sql(sql: str, table: str) -> dict[str, Any]:
    try:
        safe = _validate_select_sql(sql, table)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(safe), conn)
        return {
            "ok": True,
            "row_count_returned": len(df),
            "columns": list(df.columns),
            "rows": _rows_records(df),
        }
    except Exception as e:
        logger.warning("SQL tool execution failed: %s", e)
        return {"ok": False, "error": f"Query failed: {e!s}"}


def _tool_preview(table: str, limit: int) -> dict[str, Any]:
    lim = max(1, min(int(limit), MAX_PREVIEW_ROWS))
    sql = f'SELECT * FROM "{table}" LIMIT {lim}'
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
        return {
            "ok": True,
            "row_count_returned": len(df),
            "columns": list(df.columns),
            "rows": _rows_records(df),
        }
    except Exception as e:
        return {"ok": False, "error": f"Preview failed: {e!s}"}


def _tool_sample_stats(dataset_id: int, db: Session) -> dict[str, Any]:
    ds = _get_dataset_or_404(db, dataset_id)
    try:
        df, sampled = load_dataset_table_sample(ds, limit=ANALYSIS_ROW_CAP)
    except Exception as e:
        return {"ok": False, "error": str(e)}
    info: dict[str, Any] = {
        "ok": True,
        "row_count_total": ds.row_count,
        "sample_rows_used": len(df),
        "sampled": sampled,
        "columns": [],
    }
    for col in df.columns:
        s = df[col]
        entry: dict[str, Any] = {
            "name": str(col),
            "dtype": str(s.dtype),
            "null_count": int(s.isna().sum()),
        }
        if pd.api.types.is_numeric_dtype(s) and s.notna().any():
            sn = s.dropna()
            entry["mean"] = float(sn.mean())
            entry["min"] = float(sn.min())
            entry["max"] = float(sn.max())
        info["columns"].append(entry)
    return info


def _build_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "query_dataset_sql",
                "description": (
                    "Run a read-only SELECT against the uploaded flight-delay dataset table. "
                    "Always include a reasonable LIMIT (max 1000). Only the whitelisted table may be used."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "Single SELECT statement referencing the dataset table.",
                        },
                    },
                    "required": ["sql"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_dataset_preview",
                "description": (
                    "Fetch the first N rows from the dataset without writing SQL. "
                    "Useful to inspect raw values."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": f"Number of rows (1–{MAX_PREVIEW_ROWS}).",
                            "default": 15,
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_dataset_sample_stats",
                "description": (
                    "Return summary statistics computed on up to 100,000 rows "
                    "(full table is stored; large files are sampled automatically)."
                ),
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]


def _system_prompt(ds_context: str) -> str:
    return (
        "You are an expert data analyst assistant for DataLens, helping users explore "
        "the 2015 U.S. flight delays CSV they uploaded.\n"
        "Use the provided tools to ground every factual claim. If a tool returns an error, "
        "explain it and fix the query.\n"
        "Never invent numbers: always obtain them from tool results.\n"
        "Keep answers concise and actionable.\n\n"
        f"Dataset context:\n{ds_context}"
    )


def _dataset_context_block(db: Session, dataset_id: int) -> tuple[str, str]:
    ds = _get_dataset_or_404(db, dataset_id)
    table = ds.sqlite_table_name
    meta = json.loads(ds.columns_json)
    cols = ", ".join(f"{c['name']} ({c['dtype']})" for c in meta)
    block = (
        f"- dataset_id: {ds.id}\n"
        f"- sqlite_table_name: {table}\n"
        f"- total_rows: {ds.row_count}\n"
        f"- columns: {cols}\n"
        f"- For SQL tools, the table must appear exactly as: {table}\n"
        f"- Large tables: analytics use up to {ANALYSIS_ROW_CAP:,} rows unless you aggregate in SQL.\n"
    )
    return block, table


@router.post("/chat", response_model=ChatResponse)
def chat_with_dataset(body: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    client = _require_groq_client()
    try:
        ctx, table = _dataset_context_block(db, body.dataset_id)
    except HTTPException:
        raise

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": _system_prompt(ctx)},
    ]
    for m in body.history:
        messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": body.message})

    tools = _build_tools()

    try:
        for _ in range(MAX_TOOL_ROUNDS):
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.2,
            )
            choice = completion.choices[0]
            msg = choice.message

            if getattr(msg, "tool_calls", None):
                messages.append(
                    {
                        "role": "assistant",
                        "content": msg.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in msg.tool_calls
                        ],
                    }
                )
                for tc in msg.tool_calls:
                    name = tc.function.name
                    raw_args = tc.function.arguments or "{}"
                    try:
                        args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        result = {"ok": False, "error": "Invalid JSON in tool arguments."}
                    else:
                        if name == "query_dataset_sql":
                            result = _tool_query_sql(str(args.get("sql", "")), table)
                        elif name == "get_dataset_preview":
                            lim = int(args.get("limit", 15))
                            result = _tool_preview(table, lim)
                        elif name == "get_dataset_sample_stats":
                            result = _tool_sample_stats(body.dataset_id, db)
                        else:
                            result = {"ok": False, "error": f"Unknown tool {name!r}."}

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(result, default=str)[:120_000],
                        }
                    )
                continue

            text_out = (msg.content or "").strip()
            if not text_out:
                raise HTTPException(
                    status_code=502,
                    detail="The model returned an empty answer. Try rephrasing your question.",
                )
            return ChatResponse(
                answer=text_out,
                dataset_id=body.dataset_id,
                model=GROQ_MODEL,
            )

        raise HTTPException(
            status_code=502,
            detail="Tool loop exceeded maximum rounds without a final answer.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Groq chat failed")
        raise HTTPException(
            status_code=502,
            detail=f"Chat request failed: {e!s}",
        ) from e
#   C h a t   R o u t e r  
 