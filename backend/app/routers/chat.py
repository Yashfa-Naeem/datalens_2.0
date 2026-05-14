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
        context = f"Dataset has {len(df)} rows and columns: {list(df.columns)}. Sample: {df.head(3).to_string()}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are a data analyst. Answer questions about this flight delays dataset: {context}"},
                {"role": "user", "content": request.message}
            ]
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))