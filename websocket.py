from fastapi import WebSocket, APIRouter
from fastapi.websockets import WebSocketDisconnect
from llm_manager import LLMEngine
import json
from prompts import format_input, load_tools_metadata
from utils.logger import CustomLogger
logger = CustomLogger(__name__)

def call_function(name: str, args: dict) -> str:
    logger.debug("OUTPUT name: %s, args: %d", name, args)
    import re
    args[0] = re.sub(r'\\([a-zA-Z]+)', r'\1', args[0])
    match name:
        case "CalculatorRequest":
            from agency.calculator import calculator, CalculatorRequest
            validated_request = CalculatorRequest(**args)
            logger.debug("VALIDATED REQUEST: %s",validated_request)
            return calculator(validated_request)
        case "DateTimeRequest":
            from agency.time_managment import datetime_now, DateTimeRequest
            validated_request = DateTimeRequest(**args)
            logger.debug("VALIDATED REQUEST: %s",validated_request)
            return datetime_now(validated_request)
    logger.error("Unknown function name: %s", name)
    raise ValueError(f"Unknown function name: {name}")

websocket_router = APIRouter(
    prefix="",
    tags=["websocket"]
)

@websocket_router.websocket("/stream")
async def stream_websocket(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_json()
            parsed_data = json.loads(data) if isinstance(data, str) else data
            logger.debug("Parsed data: %s", parsed_data)
            await stream_model_response(parsed_data, websocket)
    except WebSocketDisconnect:
        logger.exception("WebSocket disconnected.")
    except Exception as e:
        logger.exception(f"General error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except Exception as send_error:
            logger.exception(f"Error sending error response: {send_error}")
    finally:
        await websocket.close()


async def stream_model_response(inputs: list[dict], websocket: WebSocket):
    try:
        prompt = format_input(inputs)
        tools = load_tools_metadata()

        engine = LLMEngine()
        response = engine.infer(
            prompt,
            stream=False,
            tools=tools,
            max_tokens=512,
            stop=["<|im_end|>"],
            temperature=0.8,
            top_p=0.95,
            top_k=40
        )
        logger.debug("Response from inference: %s", response)

        input_messages = []

        for choice in response.get("choices", []):
            message = choice.get("message", {})
            tool_calls = message.get("tool_calls", [])
            for tool_call in tool_calls:
                if tool_call.get("type") != "function":
                    continue

                name = tool_call["function"]["name"].rstrip(":")
                args = json.loads(tool_call["function"]["arguments"])
                result = call_function(name, args)
                input_messages.append({
                    "type": "function_call_output",
                    "call_id": tool_call.get("id"),
                    "output": str(result)
                })

        if input_messages:
            response["function_call_outputs"] = input_messages

        await websocket.send_json({"token": response})
    except Exception as e:
        logger.exception("LLM streaming failed")
        await websocket.send_json({"error": str(e)})
        await websocket.close(code=1011)