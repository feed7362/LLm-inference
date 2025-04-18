from llama_cpp import Llama
from utils.config import ModelSettings
from threading import Lock

from utils.logger import CustomLogger
logger = CustomLogger(__name__)

class LLMEngine:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                logger.info("Creating a new instance of LLMEngine")
                cls._instance = super(LLMEngine, cls).__new__(cls)
                cls._instance._load_model()
        return cls._instance

    def __init__(self):
        if not getattr(self, '_initialized', False):
            self._initialized = True

    def __del__(self):
        if hasattr(self, 'model'):
            try:
                del self.model
            except Exception as e:
                logger.error(f"Error cleaning up model resources: {e}")

    def _load_model(self):
        try:
            logger.info("Loading LLM model...")
            self.model = Llama(**ModelSettings().model_dump())
        except Exception as e:
            logger.exception(f"Failed to load model: {e}")
            self._initialized = False
            raise RuntimeError(f"Model initialization failed: {e}")

    def infer(self, messages: list, tools: list, stream: bool = False, **kwargs):
        if not self._initialized or not hasattr(self, 'model'):
            raise RuntimeError("Model not properly initialized")

        if not messages:
            raise ValueError("Messages list cannot be empty")

        logger.info(f"Running inference with prompt: {messages}")
        return self.model.create_chat_completion(messages, 
                                                 tools=tools or [], 
                                                 tool_choice="auto" if stream == False else [tool["function"]["name"] for tool in tools], 
                                                 stream=stream,
                                                 **kwargs)

    def warmup(self):
        try:
            logger.info("Warming up the model...")
            prompt = [{"role": "user","content": [{"type" : "text", "text": "Hi"}]}]
            self.model.create_chat_completion(messages=prompt, max_tokens=1, temperature=0.0, top_p=0.1)
        except Exception as e:
            logger.error(f"Warmup failed: {e}")

    def close(self):
        """Explicit cleanup method for releasing model resources."""
        if hasattr(self, 'model'):
            try:
                del self.model
                logger.info("Model resources have been released.")
            except Exception as e:
                logger.error(f"Error during explicit cleanup of model resources: {e}")
