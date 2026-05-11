"""Dataset profiling: types, nulls, basic statistics (sampled for large tables)."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db

from .data import _get_dataset_or_404
from .upload import ANALYSIS_ROW_CAP, load_dataset_for_profile

logger = logging.getLogger(__name__)

router = APIRouter(tags=["profile"])


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    null_count: int
    non_null_count: int
    unique_count: int | None = None
    min_value: str | float | int | None = None
    max_value: str | float | int | None = None
    mean: float | None = None
    median: float | str | None = None


class ProfileResponse(BaseModel):
    dataset_id: int
    row_count_total: int
    analysis_row_count: int
    sampled_for_analysis: bool = Field(
        ...,
        description="True if statistics are computed on the first rows only (large dataset).",
    )
    analysis_row_cap: int = ANALYSIS_ROW_CAP
    columns: list[ColumnProfile]


def _jsonable_scalar(v: Any) -> Any:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return v


def _profile_column(series: pd.Series) -> ColumnProfile:
    name = str(series.name)
    dtype = str(series.dtype)
    null_count = int(series.isna().sum())
    n = len(series)
    non_null = n - null_count
    s = series.dropna()

    unique_count: int | None
    try:
        unique_count = int(s.nunique(dropna=True)) if non_null else 0
    except Exception:
        unique_count = None

    min_v: Any = None
    max_v: Any = None
    mean_v: float | None = None
    median_v: Any = None

    if non_null == 0:
        return ColumnProfile(
            name=name,
            dtype=dtype,
            null_count=null_count,
            non_null_count=non_null,
            unique_count=unique_count,
        )

    if pd.api.types.is_numeric_dtype(series):
        min_v = _jsonable_scalar(s.min())
        max_v = _jsonable_scalar(s.max())
        mean_v = float(s.mean()) if len(s) else None
        med = s.median()
        median_v = _jsonable_scalar(med)
    elif pd.api.types.is_datetime64_any_dtype(series):
        min_v = _jsonable_scalar(pd.Timestamp(s.min()).to_pydatetime())
        max_v = _jsonable_scalar(pd.Timestamp(s.max()).to_pydatetime())
        mean_v = None
        median_v = None
    else:
        # strings / categories / mixed
        try:
            min_v = str(s.min()) if len(s) else None
            max_v = str(s.max()) if len(s) else None
        except Exception:
            min_v = max_v = None
        mean_v = None
        median_v = None

    return ColumnProfile(
        name=name,
        dtype=dtype,
        null_count=null_count,
        non_null_count=non_null,
        unique_count=unique_count,
        min_value=min_v,
        max_value=max_v,
        mean=mean_v,
        median=median_v,
    )


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    dataset_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    try:
        ds = _get_dataset_or_404(db, dataset_id)
        df, sampled = load_dataset_for_profile(ds)
        if df.empty and ds.row_count > 0:
            raise HTTPException(
                status_code=500,
                detail="Dataset metadata reports rows but query returned no data.",
            )

        columns = [_profile_column(df[c]) for c in df.columns]
        return ProfileResponse(
            dataset_id=ds.id,
            row_count_total=ds.row_count,
            analysis_row_count=len(df),
            sampled_for_analysis=sampled,
            columns=columns,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Profiling failed")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to build data profile: {e!s}",
        ) from e
