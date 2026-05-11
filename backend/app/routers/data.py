"""Paginated read access to uploaded datasets."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import engine, get_db
from ..models import Dataset

logger = logging.getLogger(__name__)

router = APIRouter(tags=["data"])

MAX_PAGE_SIZE = 500


class PaginatedDataResponse(BaseModel):
    dataset_id: int
    page: int
    page_size: int
    total_rows: int
    total_pages: int
    columns: list[str]
    rows: list[dict[str, Any]]


def _get_dataset_or_404(db: Session, dataset_id: int) -> Dataset:
    ds = db.get(Dataset, dataset_id)
    if ds is None:
        raise HTTPException(
            status_code=404,
            detail=f"No dataset found with id={dataset_id}. Upload a CSV first.",
        )
    if not re.fullmatch(r"dataset_\d+", ds.sqlite_table_name):
        raise HTTPException(
            status_code=500,
            detail="Dataset metadata is corrupt (invalid table name).",
        )
    expected = f"dataset_{ds.id}"
    if ds.sqlite_table_name != expected:
        raise HTTPException(
            status_code=500,
            detail="Dataset metadata is corrupt (table name does not match id).",
        )
    return ds


def _rows_to_jsonable(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in records:
        clean: dict[str, Any] = {}
        for k, v in row.items():
            if v is None or (isinstance(v, float) and np.isnan(v)):
                clean[k] = None
            elif isinstance(v, (np.integer,)):
                clean[k] = int(v)
            elif isinstance(v, (np.floating,)):
                clean[k] = float(v)
            elif isinstance(v, np.bool_):
                clean[k] = bool(v)
            elif hasattr(v, "isoformat"):
                clean[k] = v.isoformat()
            else:
                clean[k] = v
        out.append(clean)
    return out


@router.get("/data", response_model=PaginatedDataResponse)
def get_paginated_data(
    dataset_id: int = Query(..., ge=1, description="Dataset id returned from /api/upload"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
) -> PaginatedDataResponse:
    try:
        ds = _get_dataset_or_404(db, dataset_id)
        table = ds.sqlite_table_name
        total = ds.row_count
        if total == 0:
            raise HTTPException(
                status_code=404,
                detail="Dataset exists but contains no rows.",
            )

        total_pages = max(1, (total + page_size - 1) // page_size)
        if page > total_pages:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Page {page} is out of range. "
                    f"Valid pages are 1–{total_pages} for page_size={page_size}."
                ),
            )

        offset = (page - 1) * page_size
        sql = text(f'SELECT * FROM "{table}" LIMIT :lim OFFSET :off')
        with engine.connect() as conn:
            df = pd.read_sql(sql, conn, params={"lim": page_size, "off": offset})

        meta = json.loads(ds.columns_json)
        columns = [str(c["name"]) for c in meta]
        records = df.replace({np.nan: None}).to_dict(orient="records")
        rows = _rows_to_jsonable(records)

        return PaginatedDataResponse(
            dataset_id=ds.id,
            page=page,
            page_size=page_size,
            total_rows=total,
            total_pages=total_pages,
            columns=columns,
            rows=rows,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to read paginated data")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read dataset: {e!s}",
        ) from e
