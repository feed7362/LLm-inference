from fastapi import WebSocket, APIRouter
from fastapi.websockets import WebSocketDisconnect
from agency_manager import extract_function_outputs
from llm_manager import LLMEngine
import json
from prompts import format_input, load_tools_metadata

from utils.logger import CustomLogger
logger = CustomLogger(__name__)

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
        logger.debug("Formatted prompt: %s", prompt)
        
        engine = LLMEngine()
        response = engine.infer(
            prompt,
            stream=False,
            tools=tools,
            max_tokens=512,
            stop=["<|im_end|>"],
            temperature=0.7,
            top_p=0.90,
            top_k=40
        )
        logger.debug("Response from inference: %s", response)
        if "function_call"  in response["choices"][0]["message"]:
            function_outputs = extract_function_outputs(response)
            response["choices"][0]["message"]["function_call_outputs"] = function_outputs
            

        await websocket.send_json({"token": response})
    except Exception as e:
        logger.exception("LLM streaming failed")
        await websocket.send_json({"error": str(e)})
        await websocket.close(code=1011)