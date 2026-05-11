"""Executive summary of an uploaded dataset via Groq."""

from __future__ import annotations

import json
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from groq import Groq
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from .data import _get_dataset_or_404
from .upload import ANALYSIS_ROW_CAP, load_dataset_table_sample

logger = logging.getLogger(__name__)

router = APIRouter(tags=["summary"])

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


class SummaryResponse(BaseModel):
    dataset_id: int
    summary: str
    model: str
    context_rows_used: int = Field(
        ...,
        description="Rows from SQLite used as context (capped for large datasets).",
    )
    total_rows_in_dataset: int


def _require_groq_client() -> Groq:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not set. Add it to your environment to use /api/summary.",
        )
    return Groq(api_key=key)


@router.get("/summary", response_model=SummaryResponse)
def get_executive_summary(
    dataset_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    client = _require_groq_client()
    try:
        ds = _get_dataset_or_404(db, dataset_id)
        df, sampled = load_dataset_table_sample(ds, limit=ANALYSIS_ROW_CAP)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Failed loading dataset for summary")
        raise HTTPException(
            status_code=500,
            detail=f"Could not load dataset sample: {e!s}",
        ) from e

    meta = json.loads(ds.columns_json)
    col_lines = [f"- {c['name']}: {c['dtype']}" for c in meta]

    describe = df.describe(include="all").to_string()[:25_000]
    sample_csv = df.head(30).to_csv(index=False)[:15_000]

    user_prompt = (
        "Write an executive summary for business stakeholders.\n"
        "Include: what the dataset appears to represent, key dimensions, "
        "data quality notes (missing values if obvious from describe), "
        "and 3–5 concrete analytical angles they could explore next.\n"
        "Do not fabricate domain facts not supported by the sample below.\n\n"
        f"Total rows in database: {ds.row_count}\n"
        f"Rows provided for this summary: {len(df)}"
        f"{' (sampled from the beginning of the table)' if sampled else ''}.\n\n"
        "Column metadata:\n"
        + "\n".join(col_lines)
        + "\n\npandas.describe() on the provided rows:\n"
        + describe
        + "\n\nFirst 30 rows (CSV):\n"
        + sample_csv
    )

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior analyst summarizing tabular flight-delay style data. "
                        "Be precise, avoid hype, and call out uncertainty when the sample may not "
                        "represent the full file."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.35,
            max_tokens=1_024,
        )
        text = (completion.choices[0].message.content or "").strip()
        if not text:
            raise HTTPException(
                status_code=502,
                detail="The summarization model returned an empty response.",
            )
        return SummaryResponse(
            dataset_id=ds.id,
            summary=text,
            model=GROQ_MODEL,
            context_rows_used=len(df),
            total_rows_in_dataset=ds.row_count,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Groq summary failed")
        raise HTTPException(
            status_code=502,
            detail=f"Summary generation failed: {e!s}",
        ) from e
