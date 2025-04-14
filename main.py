from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
import json
from model import model
from tools import load_tools_metadata, calculator, datetime_now

from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    dummy_prompt = "<|im_start|>user\nHello<|im_end|>\n<|im_start|>assistant"
    _ = model(
        dummy_prompt,
        max_tokens=1,
        temperature=0.1,
        top_p=0.1,
    )
    print("Model warmed up.")

    yield

model_app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:2222",
    "http://127.0.0.1:2222",
]

model_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
    "Authorization"],
)

def build_function_tool_prompt(tools_block: str) -> str:
    return f"""
    You may call one or more functions to assist with the user query.
    
    Function signatures are provided below:
    
    <tools>
    {tools_block}
    </tools>
    
    For each function call, return a JSON object within <tool_call></tool_call> XML tags:
    
    <tool_call>
    {{"name": "<function-name>", "arguments": <args-json-object>}}
    </tool_call>
    """


def build_prompt(user_input: str) -> str:    
    system_prompt = f"""<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.
    Format all mathematical expressions using LaTeX syntax. 
    - Use `\\( ... \\)` for inline math.
    - Use `$$ ... $$` for display math blocks.
    - Do not explain LaTeX, just use it to present math.
    {build_function_tool_prompt(load_tools_metadata())}
    <|im_end|>."""
    user_prompt = f"<|im_start|>user\n{user_input.strip()}<|im_end|>"
    assistant_prompt = "<|im_start|>assistant"
    return f"{system_prompt}\n{user_prompt}\n{assistant_prompt}"


async def stream_model_response(query: str, websocket: WebSocket):
    try:
        prompt = build_prompt(query)
        response = model(
                    prompt,
                    max_tokens=512,
                    stop=["<|im_end|>"],
                    temperature=0.8,
                    top_p=0.95,
                    top_k=40,
                    stream=True)
        for chunk in response:
            print("Chunk debug: ",chunk)
            output_text = chunk["choices"][0]["text"]
            await websocket.send_json(output_text)
        await websocket.send_json({"end_of_stream": True})
    except Exception as e:
        await websocket.send_json(f"error: {str(e)}")
        await websocket.close(code=1006)


@model_app.websocket("/stream")
async def stream_websocket(websocket : WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_json()
            parsed_data = json.loads(data) if isinstance(data, str) else data
            await stream_model_response(parsed_data["text"], websocket)
    except WebSocketDisconnect:
        print("WebSocket disconnected.")
    except Exception as e:
        print(f"General error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
        await websocket.close()