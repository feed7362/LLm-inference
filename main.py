from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llm_manager import LLMEngine
from websocket import websocket_router
from prompts import validate_metadata
from contextlib import asynccontextmanager

from utils.logger import CustomLogger
logger = CustomLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Lifespan: start")
        engine = LLMEngine()
        engine.warmup()
        logger.info("Lifespan: warmup complete")

        validate_metadata()
        logger.info("Lifespan metadata validate complete")
        yield
        engine.close()
    except Exception as e:
        logger.exception(f"Lifespan error: {str(e)}")
        raise

model_app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:2222",
    "http://127.0.0.1:2222",
]

model_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
    "Authorization"],
)
model_app.include_router(websocket_router)