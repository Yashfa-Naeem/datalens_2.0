"""FastAPI application entrypoint for DataLens."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .models import Base
from .routers import chat, data, profile, summary, upload


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Import models so metadata registers before create_all
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="DataLens API", version="0.1.0", lifespan=lifespan)

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


@app.get("/api/health")
def health():
    return {"status": "ok"}
