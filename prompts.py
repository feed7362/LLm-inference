import json

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
    BaseMessage,
)
from langchain_core.prompts import ChatPromptTemplate

from llm_manager import load_tools_from_folder
from utils.logger import CustomLogger

logger = CustomLogger(__name__)

tool_list = load_tools_from_folder("./tools", package_prefix="tools")
tool_schemas = "\n".join(
    [
        f"- {tool.name}: {tool.description.replace('{', '{{').replace('}', '}}')}"
        for tool in tool_list
    ]
)
logger.debug("Tool schemas loaded: %s", tool_schemas)


def format_input(messages: str):
    system_message = f"""
        You are a helpful assistant that can use tools to get information for the user.
        
        # Content Safety:
        Avoid responding to prompts that could:
        - Involve hate speech, abuse, or discriminatory content
        - Violate privacy or generate false/misleading claims
        - Involve prohibited use-cases (see Gemma Prohibited Use Policy)
        
        If a prompt seems unsafe, ambiguous, or unethical:
        - Respond with a clarifying question, or politely refuse if necessary
        - Do not generate code that could be used for harmful purposes
        
        Follow these guidelines:
        - Prefer to respond directly if you can answer confidently from your own knowledge.
        - Use tools only when the answer requires up-to-date, external, or procedural data.
        - Think carefully about which tool to use based on its description and input schema.
        - Be transparent: after using a tool, explain what the result means to the user.
        - If no tool is appropriate, continue the conversation or ask for clarification.
        - Answer the user's questions based on the below context. 
        - Use tools only when the answer requires up-to-date, external, or procedural data
        - If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":
        
        # Your responsibilities include
        - Always provide concise, accurate, and respectful responses
        - Avoid generating or amplifying misinformation, harmful content, or biased representations
        - Clearly state when you are uncertain or when external information is needed
        - Do not fabricate facts or simulate sensitive information such as personal data
        
        # Limitations to be aware of
        - You are not a factual database; you generate text based on patterns in your training data
        - Your training data may contain biases or gaps—apply caution, and encourage verification
        - You may struggle with sarcasm, metaphor, or nuanced emotional tone
        - You perform best when tasks are clearly framed and contextually rich
        
        # Tools
        You may call one or more functions to assist with the user query.
        You are provided with function signatures within <tools></tools> XML tags:
        <tools>
        {tool_schemas}
        </tools>
        For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags.
        
        # Latex Formatting
        Format all mathematical expressions using LaTeX syntax:\n
        - Use `\\( ... \\)` for inline math.\n
        - Use `$$ ... $$` for display math blocks.\n
        - Do not explain LaTeX, only use it to present math.
        """.strip()
    logger.info("Prompt template created successfully.")

    logger.debug("user_message: %s", messages)
    prompt = ChatPromptTemplate.from_messages(
        [SystemMessage(content=system_message), HumanMessage(content=messages)]
    )
    logger.debug("Prompt: %s", prompt)

    return prompt


def schema_validation(message: BaseMessage) -> dict | None:
    if isinstance(message, SystemMessage):
        return None
    elif isinstance(message, HumanMessage):
        return None
    elif isinstance(message, AIMessage):
        if "tool_calls" in message.additional_kwargs:
            tool_calls = []
            for tool_call in message.additional_kwargs["tool_calls"]:
                tool_calls.append(
                    {
                        "id": tool_call["id"],
                        "type": "function",
                        "function": {
                            "name": tool_call["function"]["name"].rstrip(":"),
                            "arguments": tool_call["function"]["arguments"],
                        },
                    }
                )
            return {
                "role": "assistant",
                "content": str(message.content) or "",
                "tool_calls": tool_calls,
            }
        else:
            return {"role": "assistant", "content": str(message.content) or ""}
    elif isinstance(message, ToolMessage):
        content_str = message.content
        content_json = "{}"
        if isinstance(content_str, str):
            try:
                parsed = json.loads(content_str.replace("'", '"'))
                content_json = json.dumps(parsed)
            except Exception as e:
                content_json = "{}"
                logger.error("Failed to parse tool message content: %s", e)
        return {
            "role": "tool",
            "tool_call_id": message.tool_call_id,
            "name": message.name,
            "content": content_json or "",
        }
    else:
        return {
            "role": "unknown",
            "content": str(getattr(message, "content", "")) or "",
        }
