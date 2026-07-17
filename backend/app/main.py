from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base  # noqa: F401 — ensures all models are registered

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (safe no-op if they already exist)
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Fix CORS: when allow_origins=["*"], allow_credentials MUST be False for browsers to accept it.
# Since we use Bearer tokens (not cookies), allow_credentials=False is perfectly fine.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to SubFlow API"}
