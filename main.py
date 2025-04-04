from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
from pkg_resources import yield_lines

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
        prompt = f"You are a helpful assistant. Q: {query} ? A:"
        response = model(
                    prompt,
                    max_tokens=512,
                    stop=["<|endoftext|>", "?", "Q:", "A:"],
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    stream=True)
        for chunk in response:
            print("Chunk debug: ",chunk)
            output_text = chunk["choices"][0]["text"]
            await websocket.send_json(output_text)
        return None
    except Exception as e:
        await websocket.send_json(f"error: {str(e)}")
        return None


@model_app.websocket("/stream")
async def stream_websocket(websocket : WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_json()

            await stream_model_response(data, websocket)

    except WebSocketDisconnect:
        print("WebSocket disconnected.")
    except Exception as e:
        print(f"General error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
        await websocket.close()