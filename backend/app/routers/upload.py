"""CSV upload: validate, persist full data to SQLite, return column info and stats."""

from __future__ import annotations

import io
import json
import logging
import re

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import engine, get_db
from ..models import Dataset

logger = logging.getLogger(__name__)

router = APIRouter(tags=["upload"])

MAX_UPLOAD_BYTES = 50 * 1024 * 1024
CHUNK_ROWS = 50_000
ANALYSIS_ROW_CAP = 100_000


class ColumnInfo(BaseModel):
    name: str
    dtype: str


class NumericColumnStats(BaseModel):
    name: str
    min: float | int | None = None
    max: float | int | None = None
    mean: float | None = None
    null_count: int = 0


class UploadResponse(BaseModel):
    dataset_id: int
    filename: str
    row_count: int
    column_count: int
    sqlite_table_name: str
    columns: list[ColumnInfo]
    numeric_stats: list[NumericColumnStats]
    analysis_sample_size: int = Field(
        ...,
        description="Rows used for numeric_stats (capped for large datasets).",
    )
    stored_full_dataset: bool = True
    message: str | None = None


def _sanitize_table_suffix(dataset_id: int) -> str:
    if dataset_id < 1:
        raise HTTPException(status_code=500, detail="Invalid dataset id for table name.")
    return f"dataset_{dataset_id}"


def _validate_table_name(name: str, dataset_id: int) -> None:
    expected = _sanitize_table_suffix(dataset_id)
    if name != expected:
        raise HTTPException(status_code=500, detail="Internal table name mismatch.")
    if not re.fullmatch(r"dataset_\d+", name):
        raise HTTPException(status_code=500, detail="Invalid SQLite table name.")


def _read_csv_chunks(raw: bytes) -> tuple[pd.DataFrame, int, list[str]]:
    """Validate CSV and return (first_chunk, total_rows, column_names)."""
    try:
        bio = io.BytesIO(raw)
        peek = pd.read_csv(bio, nrows=1000, engine="c")
    except pd.errors.EmptyDataError as e:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty or not a valid CSV.",
        ) from e
    except pd.errors.ParserError as e:
        raise HTTPException(
            status_code=400,
            detail=f"CSV parse error: {e!s}",
        ) from e
    except UnicodeDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail="File must be valid UTF-8 text (CSV).",
        ) from e

    if peek.shape[1] == 0:
        raise HTTPException(
            status_code=400,
            detail="CSV has no columns. Ensure the first row contains headers.",
        )

    columns = [str(c) for c in peek.columns.tolist()]
    if len(set(columns)) != len(columns):
        raise HTTPException(
            status_code=400,
            detail="CSV contains duplicate column names. Please use unique headers.",
        )

    bio = io.BytesIO(raw)
    total = 0
    first: pd.DataFrame | None = None
    try:
        for i, chunk in enumerate(pd.read_csv(bio, chunksize=CHUNK_ROWS, engine="c")):
            if i == 0:
                first = chunk.copy()
            total += len(chunk)
    except (pd.errors.ParserError, UnicodeDecodeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read full CSV: {e!s}",
        ) from e

    if total == 0:
        raise HTTPException(
            status_code=400,
            detail="CSV contains no data rows.",
        )

    assert first is not None
    return first, total, columns


def _numeric_stats_from_frame(df: pd.DataFrame) -> list[NumericColumnStats]:
    stats: list[NumericColumnStats] = []
    for col in df.columns:
        s = df[col]
        if not pd.api.types.is_numeric_dtype(s):
            continue
        null_count = int(s.isna().sum())
        clean = s.dropna()
        if len(clean) == 0:
            stats.append(
                NumericColumnStats(name=str(col), null_count=null_count),
            )
            continue
        stats.append(
            NumericColumnStats(
                name=str(col),
                min=float(clean.min()) if len(clean) else None,
                max=float(clean.max()) if len(clean) else None,
                mean=float(clean.mean()) if len(clean) else None,
                null_count=null_count,
            ),
        )
    return stats


def _drop_table(conn, table: str) -> None:
    if not re.fullmatch(r"dataset_\d+", table):
        raise ValueError(f"Refusing to drop invalid table name: {table!r}")
    conn.execute(text(f'DROP TABLE IF EXISTS "{table}"'))


@router.post("/upload", response_model=UploadResponse)
def upload_csv(
    file: UploadFile = File(..., description="CSV file, max 50MB"),
    db: Session = Depends(get_db),
) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename.")

    lower = file.filename.lower()
    if not lower.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only .csv files are accepted.",
        )

    try:
        raw_chunks: list[bytes] = []
        total_size = 0
        while True:
            block = file.file.read(1024 * 1024)
            if not block:
                break
            total_size += len(block)
            if total_size > MAX_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail="File exceeds the maximum allowed size of 50MB.",
                )
            raw_chunks.append(block)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed reading upload")
        raise HTTPException(
            status_code=400,
            detail=f"Could not read uploaded file: {e!s}",
        ) from e

    raw = b"".join(raw_chunks)
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        first_chunk, row_count, columns = _read_csv_chunks(raw)
    except HTTPException:
        raise

    column_count = len(columns)
    dtypes = {str(c): str(first_chunk[c].dtype) for c in first_chunk.columns}

    dataset = Dataset(
        original_filename=file.filename,
        row_count=0,
        column_count=column_count,
        columns_json=json.dumps(
            [{"name": n, "dtype": dtypes.get(n, "unknown")} for n in columns]
        ),
        sqlite_table_name="",
    )
    db.add(dataset)
    db.flush()
    table_name = _sanitize_table_suffix(dataset.id)
    dataset.sqlite_table_name = table_name
    dataset.row_count = row_count
    db.commit()

    try:
        bio = io.BytesIO(raw)
        first_written = False
        for chunk in pd.read_csv(bio, chunksize=CHUNK_ROWS, engine="c"):
            if not first_written:
                chunk.to_sql(
                    table_name,
                    con=engine,
                    if_exists="replace",
                    index=False,
                    method="multi",
                )
                first_written = True
            else:
                chunk.to_sql(
                    table_name,
                    con=engine,
                    if_exists="append",
                    index=False,
                    method="multi",
                )
    except Exception as e:
        logger.exception("Failed writing CSV to SQLite")
        try:
            with engine.begin() as conn:
                _drop_table(conn, table_name)
        except Exception:
            logger.exception("Cleanup drop table failed")
        db.delete(dataset)
        db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store dataset in the database: {e!s}",
        ) from e

    analysis_sql = f'SELECT * FROM "{table_name}" LIMIT {ANALYSIS_ROW_CAP}'
    try:
        with engine.connect() as conn:
            analysis_df = pd.read_sql(text(analysis_sql), conn)
    except Exception as e:
        logger.exception("Failed loading analysis sample after upload")
        raise HTTPException(
            status_code=500,
            detail=f"Dataset stored but analysis sample failed: {e!s}",
        ) from e

    sample_size = len(analysis_df)
    numeric_stats = _numeric_stats_from_frame(analysis_df)

    msg: str | None = None
    if row_count > ANALYSIS_ROW_CAP:
        msg = (
            f"Full {row_count:,} rows are stored in SQLite. "
            f"Numeric statistics use the first {sample_size:,} rows."
        )

    return UploadResponse(
        dataset_id=dataset.id,
        filename=file.filename,
        row_count=row_count,
        column_count=column_count,
        sqlite_table_name=table_name,
        columns=[ColumnInfo(name=c["name"], dtype=c["dtype"]) for c in json.loads(dataset.columns_json)],
        numeric_stats=numeric_stats,
        analysis_sample_size=sample_size,
        stored_full_dataset=True,
        message=msg,
    )


def load_dataset_table_sample(
    dataset: Dataset, limit: int = ANALYSIS_ROW_CAP
) -> tuple[pd.DataFrame, bool]:
    """Load up to `limit` rows for analysis. Returns (dataframe, sampled)."""
    _validate_table_name(dataset.sqlite_table_name, dataset.id)
    if limit < 1:
        raise ValueError("limit must be at least 1")
    sql = text(f'SELECT * FROM "{dataset.sqlite_table_name}" LIMIT :lim')
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"lim": limit})
    sampled = dataset.row_count > limit
    return df, sampled


def load_dataset_for_profile(dataset: Dataset) -> tuple[pd.DataFrame, bool]:
    cap = min(ANALYSIS_ROW_CAP, max(1, dataset.row_count))
    return load_dataset_table_sample(dataset, limit=cap)
#   C S V   U p l o a d   R o u t e r  
 