from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, data, profile, chat, summary, aggregate
app = FastAPI(title="DataLens API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(upload.router, prefix="/api")
app.include_router(data.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(aggregate.router, prefix="/api")
@app.get("/api/health")
def health():
    return {"status": "ok"}