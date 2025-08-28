import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from media_api.core.database import engine
from media_api.core.models import Base
from media_api.routers import media_files, media_streams


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown


app = FastAPI(
    title="Media API",
    description="API service for managing media content, primarily focused on video assets",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(media_files.router)
app.include_router(media_streams.router)


@app.get("/")
async def root():
    return {"message": "Media API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True
    )
