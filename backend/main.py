from fastapi import FastAPI
from contextlib import asynccontextmanager

from config import settings
from auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting application")
    yield
    print("🛑 Shutting down application")


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
