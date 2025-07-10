import uuid
from typing import (
    Annotated,
    Sequence,
    TypedDict
)

from langgraph.constants import END
from llama_cpp_chat_model.llama_chat_model import LlamaChatModel
import importlib
import inspect
import os
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools.simple import Tool
from langgraph.graph import add_messages, StateGraph
from llama_cpp import Llama
from utils.config import ModelSettings
from threading import Lock
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from utils.logger import CustomLogger

logger = CustomLogger(__name__)


class SingletonMeta(type):
    _instances = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                logger.debug("Creating new LLMEngine instance")
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            else:
                logger.debug("Reusing existing LLMEngine instance")
        return cls._instances[cls]


class LLMEngine(metaclass=SingletonMeta):
    def __init__(self, **model_kwargs):
        self._model = None
        self._model_lock = Lock()
        self._warmup_done = False
        self._model_kwargs = model_kwargs

    def _load_model(self):
        with self._model_lock:
            if self._model is None:
                logger.info("Loading LLM model...")
                base_settings = ModelSettings().model_dump()
                self._model = LangGraphAgent(
                    internal_params=base_settings,
                    **self._model_kwargs
                )().with_config(config=RunnableConfig(configurable={
                    "thread_id": str(uuid.uuid4()),
                    "recursion_limit": 50
                }))
                logger.info("Model loaded successfully.")

    def infer(self, inputs: list, stream: bool = False):
        if not inputs:
            raise ValueError("Messages list cannot be empty")

        logger.info(f"Running inference with prompt: {inputs}")

        if stream:
            return self._model.astream(
                {"messages": inputs},
                stream_mode="values"
            )
        else:
            return self._model.invoke(
                {"messages": inputs}
            )

    def warmup(self):
        try:
            self._load_model()
            logger.info("Warming up the model...")
            self._model.invoke({
                "messages": [HumanMessage(content="Hello")]
            })
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


class AgentState(TypedDict):
    """The state of the agent."""
    # add_messages is a reducer
    # See https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers
    messages: Annotated[Sequence[BaseMessage], add_messages]


class LangGraphAgent(metaclass=SingletonMeta):
    def __init__(self, internal_params: dict | None = None, **model_kwargs):
        if internal_params is None:
            internal_params = {}

        self.tool_list = load_tools_from_folder("./tools", package_prefix="tools")
        logger.debug(f"Loaded tools: {[tool.name for tool in self.tool_list]}")

        self.tool_node = ToolNode(self.tool_list, handle_tool_errors=True)
        self.model = Llama(**internal_params)
        self.chat_model = LlamaChatModel(llama=self.model)

        self.llm_with_tools = self.chat_model.bind_tools(tools=self.tool_list, tool_choice="auto").with_config(
            config=RunnableConfig(configurable={"temperature": 0.0}))

        self.llm = self.chat_model.with_config(
            config=RunnableConfig(configurable={**model_kwargs}))

        self.app = self._build_workflow()

    def _build_workflow(self):
        def should_continue(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]

            if isinstance(last_message, AIMessage) and getattr(last_message, "tool_calls", None):
                return "continue"
            else:
                return "end"

        def call_model(state: AgentState, config: RunnableConfig):
            messages = state["messages"]

            if isinstance(messages[-1], ToolMessage):
                sys = SystemMessage(
                    content=(
                        f"""
                        Respond naturally and informatively to the user based on the tool's response. 
                        Avoid mentioning tools, JSON, or technical details. 
                        Do not prefix responses with labels like 'AI:'.
                        Tool responses {messages[-1].content}
                        """
                    )
                )

                response = self.llm.invoke(messages + [sys], config)
                if not isinstance(response, AIMessage):
                    response = AIMessage(content=response.strip())
            else:
                response = self.llm_with_tools.invoke(input=messages, config=config)

            return {"messages": [response]}

        workflow = StateGraph(AgentState)

        workflow.add_node("agent", call_model)
        workflow.add_node("tools", self.tool_node)

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent", should_continue, {"continue": "tools", "end": END}
        )

        workflow.add_edge("tools", "agent")

        checkpointer = MemorySaver()
        return workflow.compile(checkpointer=checkpointer, debug=True)

    def __call__(self, *args, **kwargs):
        return self.app


def load_tools_from_folder(folder_path: str, package_prefix: str = "") -> list[Tool]:
    tools = []

    for filename in os.listdir(folder_path):
        if not filename.endswith(".py") or filename.startswith("__"):
            continue

        module_name = filename[:-3]
        import_path = f"{package_prefix}.{module_name}" if package_prefix else module_name

        try:
            module = importlib.import_module(import_path)
        except Exception as e:
            logger.error(f"Failed to import {import_path}: {e}")
            continue

        for name, obj in inspect.getmembers(module):
            if isinstance(obj, Tool):
                tools.append(obj)
                logger.debug(f"Loaded Tool: {name} from {import_path}")
            else:
                logger.debug(f"Ignored member: {name} ({type(obj).__name__})")

    return tools
