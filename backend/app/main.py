from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import init_db
from app.api.chat import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        print("Database initialised successfully.")
    except Exception as e:
        print(f"WARNING: Database init failed: {e}")
        print("Backend will start but DB calls will fail until Postgres is available.")
    yield


app = FastAPI(title="FinStress Bot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
