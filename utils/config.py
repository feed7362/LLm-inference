from pydantic_settings import BaseSettings

class ModelSettings(BaseSettings):
    model_path: str = "models/nlp/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    chat_format: str = "chatml-function-calling"
    n_gpu_layers: int = 30
    n_threads: int = 8
    n_batch: int = 512
    use_mlock: bool = True
    use_mmap: bool = True
    n_ctx: int = 2048
    verbose: bool = True    

class DefaultInputParams(BaseSettings):
    stop: list[str] = ["<|im_end|>"]
    stream: bool = True
    repeat_penalty: float = 1.0

    class Config:
        env_prefix = "default_"

class BaseInputParams(DefaultInputParams):
    max_tokens: int = 512
    temperature: float = 0.6
    top_p: float = 0.95
    top_k: int = 40

    class Config:
        env_prefix = "base_"

class PremiumParams(DefaultInputParams):
    max_tokens: int = 1024
    temperature: float = 0.8
    top_p: float = 0.95
    top_k: int = 40

    class Config:
        env_prefix = "premium_"