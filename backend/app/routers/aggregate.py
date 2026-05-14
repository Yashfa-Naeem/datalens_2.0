from fastapi import APIRouter, HTTPException
import pandas as pd
from app.database import engine
router = APIRouter()
@router.get("/aggregate")
def aggregate(dataset_id: int = 1, airline: str = "", year: str = "", groupby: str = "airline"):
    try:
        df = pd.read_sql("SELECT * FROM dataset_main", engine)
        if airline:
            df = df[df["AIRLINE"] == airline]
        if year:
            df = df[df["YEAR"] == int(year)]
        if groupby == "airline":
            result = df.groupby("AIRLINE")["DEPARTURE_DELAY"].mean().reset_index()
            result.columns = ["name", "avg_delay"]
        elif groupby == "month":
            result = df.groupby("MONTH")["DEPARTURE_DELAY"].mean().reset_index()
            result.columns = ["name", "avg_delay"]
        elif groupby == "cancellation":
            result = df.groupby("CANCELLED").size().reset_index()
            result.columns = ["name", "value"]
        elif groupby == "airport":
            result = df.groupby("ORIGIN_AIRPORT")["DEPARTURE_DELAY"].mean().reset_index()
            result = result.nlargest(10, "DEPARTURE_DELAY")
            result.columns = ["name", "avg_delay"]
        else:
            result = df.groupby(groupby).size().reset_index()
            result.columns = ["name", "value"]
        return result.fillna(0).to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/profile/{dataset_id}")
def get_profile_by_id(dataset_id: int):
    try:
        df = pd.read_sql("SELECT * FROM dataset_main", engine)
        profile = {}
        for col in df.columns:
            col_data = {}
            col_data["type"] = str(df[col].dtype)
            col_data["null_count"] = int(df[col].isnull().sum())
            col_data["unique_count"] = int(df[col].nunique())
            if df[col].dtype in ["int64", "float64"]:
                col_data["min"] = float(df[col].min()) if not pd.isna(df[col].min()) else None
                col_data["max"] = float(df[col].max()) if not pd.isna(df[col].max()) else None
                col_data["mean"] = float(df[col].mean()) if not pd.isna(df[col].mean()) else None
            else:
                col_data["top_values"] = df[col].value_counts().head(5).to_dict()
            profile[col] = col_data
        airlines = df["AIRLINE"].unique().tolist() if "AIRLINE" in df.columns else []
        years = df["YEAR"].unique().tolist() if "YEAR" in df.columns else []
        return {"profile": profile, "row_count": len(df), "airlines": airlines, "years": years}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))