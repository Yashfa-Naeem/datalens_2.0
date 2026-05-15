from fastapi import APIRouter, HTTPException
import pandas as pd
from app.database import engine
router = APIRouter()
def get_df():
    return pd.read_sql("SELECT * FROM dataset_main", engine)
def get_categorical_cols(df):
    cats = [col for col in df.columns if str(df[col].dtype) in ["object", "string", "str"]]
    return [col for col in cats if df[col].nunique() < 50]
def get_numeric_cols(df):
    return [col for col in df.columns if str(df[col].dtype) in ["int64", "float64", "int32", "float32"]]
@router.get("/aggregate")
def aggregate(dataset_id: int = 1, groupby: str = "", filter_col: str = "", filter_val: str = ""):
    try:
        df = get_df()
        if filter_col and filter_val and filter_col in df.columns:
            df = df[df[filter_col].astype(str) == filter_val]
        cat_cols = get_categorical_cols(df)
        num_cols = get_numeric_cols(df)
        if not groupby or groupby not in df.columns:
            groupby = cat_cols[0] if cat_cols else df.columns[0]
        if num_cols:
            value_col = num_cols[0]
            result = df.groupby(groupby)[value_col].mean().reset_index()
            result.columns = ["name", "value"]
        else:
            result = df.groupby(groupby).size().reset_index()
            result.columns = ["name", "value"]
        result = result.dropna().head(20)
        return result.fillna(0).to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/profile/{dataset_id}")
def get_profile_by_id(dataset_id: int):
    try:
        df = get_df()
        profile = {}
        for col in df.columns:
            col_data = {}
            col_data["type"] = str(df[col].dtype)
            col_data["null_count"] = int(df[col].isnull().sum())
            col_data["unique_count"] = int(df[col].nunique())
            if str(df[col].dtype) in ["int64", "float64"]:
                col_data["min"] = float(df[col].min()) if not pd.isna(df[col].min()) else None
                col_data["max"] = float(df[col].max()) if not pd.isna(df[col].max()) else None
                col_data["mean"] = float(df[col].mean()) if not pd.isna(df[col].mean()) else None
            else:
                col_data["top_values"] = df[col].value_counts().head(5).to_dict()
            profile[col] = col_data
        cat_cols = [col for col in df.columns if str(df[col].dtype) in ["object", "string", "str"] and df[col].nunique() < 50]
        num_cols = [col for col in df.columns if str(df[col].dtype) in ["int64", "float64"]]
        filters = {}
        for col in cat_cols[:3]:
            filters[col] = df[col].unique().tolist()[:50]
        return {"profile": profile, "row_count": len(df), "column_count": len(df.columns), "filters": filters, "categorical_cols": cat_cols, "numeric_cols": num_cols}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))