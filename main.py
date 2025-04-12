from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
import json
from model import model

model_app = FastAPI()

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

async def stream_model_response(query: str, websocket: WebSocket):
    try:
        prompt = f"""<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>.
        <|im_start|>user
        {query.strip()}<|im_end|>
        <|im_start|>assistant"""
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