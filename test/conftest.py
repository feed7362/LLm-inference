import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from websocket_client import websocket_router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(websocket_router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)
