import json

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from datetime import date

from utils.logger import CustomLogger
logger = CustomLogger(__name__)

def format_input(messages: str):
    system_message = (
        f"""
        You are an AI assistant that can answer questions and provide information. 
        Today's date is {date.today().strftime("%B %d %Y")}
        Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
        Answer as many questions as you can using your existing knowledge.  
        If no tool is needed, answer directly.\n
        Format all mathematical expressions using LaTeX syntax:\n
        - Use `\\( ... \\)` for inline math.\n
        - Use `$$ ... $$` for display math blocks.\n
        - Do not explain LaTeX, only use it to present math.
        """
    )

    # examples = [
    #     {"input": "What's the weather in London?",
    #      "output": "{\"name\":\"get_weather_by_location\",\"arguments\":{\"location\":\"London\"}}"},
    #     {"input": "Explain Python for-loop.",
    #      "output": "{\"name\":\"retrieve_context\",\"arguments\":{\"query\":\"Python for-loop tutorial\"}}"},
    # ]
    # 
    # example_prompt = ChatPromptTemplate.from_messages([
    #     ("user", "{input}"),
    #     ("assistant", "{output}")
    # ])
    # 
    # few_shot_prompt = FewShotChatMessagePromptTemplate(
    #     examples=examples,
    #     example_prompt=example_prompt
    # )
    logger.info("Prompt template created successfully.")

    logger.debug("user_message: %s", messages)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        # few_shot_prompt,
        ("user", "{messages}")
    ])
    logger.debug("Prompt: %s", prompt)

    return prompt



def schema_validation(message: BaseMessage) -> dict:
    if isinstance(message, SystemMessage):
        pass
    elif isinstance(message, HumanMessage):
        pass
    elif isinstance(message, AIMessage):
        if "tool_calls" in message.additional_kwargs:
            tool_calls = []
            for tool_call in message.additional_kwargs["tool_calls"]:
                tool_calls.append({
                    "id": tool_call["id"],
                    "type": "function",
                    "function": {
                        "name": tool_call["function"]["name"].rstrip(':'),
                        "arguments": tool_call["function"]["arguments"],
                    }
                })
            return {
                "role": "assistant",
                "content": str(message.content) or "",
                "tool_calls": tool_calls
            }
        else:
            return {
                "role": "assistant",
                "content": str(message.content) or ""
            }
    elif isinstance(message, ToolMessage):
        content_str = message.content
        content_json = "{}"
        if isinstance(content_str, str):
            try:
                parsed = json.loads(content_str.replace("'", '"'))
                content_json = json.dumps(parsed)
            except Exception:
                content_json = "{}"
        return {
            "role": "tool",
            "tool_call_id": message.tool_call_id,
            "name": message.name,
            "content": content_json or ""
        }
    else:
        return {
            "role": "unknown",
            "content": str(getattr(message, "content", "")) or ""
        }
