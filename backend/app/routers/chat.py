from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
from app.database import engine
import os
from groq import Groq
router = APIRouter(tags=["chat"])
class ChatRequest(BaseModel):
    message: str
    dataset_id: int = 1
@router.post("/chat")
def chat(request: ChatRequest):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not set")
    try:
        df = pd.read_sql("SELECT * FROM dataset_main LIMIT 1000", engine)
        client = Groq(api_key=api_key)
        cols = list(df.columns)
        sample = df.head(5).to_string()
        stats = df.describe().to_string()
        context = f"Dataset has {len(df)} rows and {len(df.columns)} columns. Columns: {cols}. Sample data: {sample}. Statistics: {stats}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are a data analyst. Answer questions based ONLY on this dataset. Do not assume anything not in the data. Dataset info: {context}"},
                {"role": "user", "content": request.message}
            ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))