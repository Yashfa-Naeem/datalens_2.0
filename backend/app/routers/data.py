from fastapi import APIRouter, HTTPException
import pandas as pd
from app.database import engine
router = APIRouter()
@router.get("/data")
def get_data(page: int = 1, page_size: int = 100):
    try:
        offset = (page - 1) * page_size
        df = pd.read_sql("SELECT * FROM dataset_main LIMIT ? OFFSET ?", engine, params=(page_size, offset))
        return {"data": df.to_dict(orient="records"), "page": page, "page_size": page_size}
    except Exception as e:
        raise HTTPException(status_code=404, detail="No dataset found. Please upload a CSV first.")