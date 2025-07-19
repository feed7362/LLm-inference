from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv("./config/dev.env", override=True)


class ServiceSettings(BaseSettings):
    SEARCH_API_KEY: str
    CX: str

    class Config:
        env_file_encoding = 'utf-8'
        env_file = './config/prod.env'


class DatabaseSettings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    class Config:
        env_file = './config/database.env'

class ModelSettings(BaseSettings):
    model_path: str = "models/nlp/gemma-3-4b-it-qat-UD-Q5_K_XL.gguf"
    chat_format: str = "chatml-function-calling"
    n_gpu_layers: int = 32
    n_threads: int = 8
    n_batch: int = 512
    use_mlock: bool = False
    use_mmap: bool = True
    n_ctx: int = 10_000
    verbose: bool = True


service_settings = ServiceSettings()
database_settings = DatabaseSettings()
