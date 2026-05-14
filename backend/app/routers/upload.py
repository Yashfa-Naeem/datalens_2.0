from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
from app.database import engine, SessionLocal
from app.models import Base, Dataset
import json
router = APIRouter()
Base.metadata.create_all(bind=engine)
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB")
    try:
        df = pd.read_csv(io.BytesIO(content))
        if len(df) > 100000:
            df = df.sample(100000)
        table_name = "dataset_main"
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        db = SessionLocal()
        db.query(Dataset).delete()
        dataset = Dataset(filename=file.filename, table_name=table_name, columns=json.dumps(list(df.columns)), row_count=len(df))
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        dataset_id = dataset.id
        db.close()
        return {"message": "File uploaded successfully", "dataset_id": dataset_id, "rows": len(df), "columns": list(df.columns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))