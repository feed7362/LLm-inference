import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:model_app", host="0.0.0.0", port=2222, workers=2, log_level="debug")