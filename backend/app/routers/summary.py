from fastapi import APIRouter, HTTPException
import pandas as pd
from app.database import engine
import os
from groq import Groq
router = APIRouter(tags=["summary"])
@router.get("/summary")
@router.get("/summary/{dataset_id}")
def get_summary(dataset_id: int = 1):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not set")
    try:
        df = pd.read_sql("SELECT * FROM dataset_main LIMIT 1000", engine)
        client = Groq(api_key=api_key)
        cols = list(df.columns)
        stats = df.describe().to_string()
        sample = df.head(3).to_string()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a business analyst. Write a concise executive summary based only on the actual data provided."},
                {"role": "user", "content": f"Write an executive summary for this dataset. Columns: {cols}. Sample data: {sample}. Statistics: {stats}"}
            ]
        )
        return {"summary": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))