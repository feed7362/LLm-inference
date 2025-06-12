from llama_cpp import Llama

from langchain_openai.chat_models.base import BaseChatOpenAI

from llama_cpp_chat_model.llama_client import LLamaOpenAIClient
from llama_cpp_chat_model.llama_client_async import LLamaOpenAIClientAsync


class LlamaChatModel(BaseChatOpenAI):
    model_name: str = "unknown"
    llama: Llama = None

    def __init__(
        self,
        llama: Llama,
        **kwargs,
    ):
        super().__init__(
            **kwargs,
            client=LLamaOpenAIClient(llama=llama),
            async_client=LLamaOpenAIClientAsync(llama=llama),
        )
        self.llama = llama

    @property
    def _llm_type(self) -> str:
        """Return type of chat model"""
        return self.llama.model_path
