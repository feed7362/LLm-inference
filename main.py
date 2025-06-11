from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llm_manager import LLMEngine
from websocket import websocket_router
from contextlib import asynccontextmanager

from utils.logger import CustomLogger
logger = CustomLogger(__name__)

def initialize_engine() -> LLMEngine:
    params = {
        "max_tokens": 512,
        "stop": ["<|im_end|>"],
        "temperature": 0.7,
        "top_k": 40,
        "max_retries": 3,
        "top_p": 0.95,
        "frequency_penalty": 1.2,
    }
    engine = LLMEngine(**params)
    engine.warmup()
    logger.info("Engine warmup complete")
    return engine

def cleanup_engine(engine: LLMEngine) -> None:
    engine.close()
    logger.info("Engine closed")

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = None
    try:
        logger.info("Lifespan: start")
        engine = initialize_engine()
        yield
    except Exception as e:
        logger.exception(f"Lifespan error: {str(e)}")
        raise
    finally:
        if engine:
            cleanup_engine(engine)

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
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

model_app.include_router(websocket_router)