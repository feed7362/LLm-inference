from llama_cpp import Llama
from utils.config import ModelSettings
from threading import Lock

from utils.logger import CustomLogger
logger = CustomLogger(__name__)

class SingletonMeta(type):
    _instances = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class LLMEngine(metaclass=SingletonMeta):
    def __init__(self):
        self._model = None
        self._model_lock = Lock()
        self._warmup_done = False

    def _load_model(self):
        with self._model_lock:
            if self._model is None:
                logger.info("Loading LLM model...")
                self._model = Llama(**ModelSettings().model_dump())
                logger.info("Model loaded successfully.")

    def infer(self, messages: list, tools: list, stream: bool = False, **kwargs):
        if not messages:
            raise ValueError("Messages list cannot be empty")

        logger.info(f"Running inference with prompt: {messages}")

        tool_choice = "none" if stream else "auto"

        return self._model.create_chat_completion(
            messages,
            tools=tools or [],
            tool_choice=tool_choice,
            stream=stream,
            **kwargs
        )

    def warmup(self):
        try:
            self._load_model()
            logger.info("Warming up the model...")
            prompt = [{"role": "user", "content": [{"type": "text", "text": "Hi"}]}]
            self._model.create_chat_completion(messages=prompt, max_tokens=1, temperature=0.0, top_p=0.1)
            self._warmup_done = True
            logger.info("Warmup complete.")
        except Exception as e:
            logger.error(f"Warmup failed: {e}")

    def close(self):
        with self._model_lock:
            if self._model is not None:
                try:
                    del self._model
                    logger.info("Model resources have been released.")
                except Exception as e:
                    logger.error(f"Error cleaning up model resources: {e}")
                finally:
                    self._model = None
                    self._warmup_done = False
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()