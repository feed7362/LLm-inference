# LLM-Inference

**LLM-Inference** is a FastAPI-based backend for large language model inference over a WebSocket API. Built with LangChain, LangGraph, and llama-cpp-python, it supports OpenAI-compatible local models (e.g., Gemma 3B via llama.cpp) and provides infrastructure for tool-augmented agents including RAG, code execution, and more.

---

## 🚀 Features

- 🔁 **OpenAI-compatible**: Designed for compatibility with OpenAI-style API and tools ecosystem.
- 🧠 **Local LLM support**: Optimized for models like Gemma 3B, served through `llama-cpp-python`.
- 🔧 **Tool use via LangChain**: Code execution, calculator, weather, and custom tools (experimental).
- 🌐 **WebSocket API**: Real-time inference with client-server communication over WS.
- 🧱 **LangGraph agent support**: Supports multistep agent workflows.
- 🐳 **Docker-native**: Lightweight multi-stage Docker build reduces final image size.
- ⚙️ **Devcontainer support**: Preconfigured for VSCode DevContainers.

---

## 📦 Tech Stack

| Component     | Technology           |
|---------------|----------------------|
| API Backend   | FastAPI (async)      |
| Inference     | llama-cpp-python     |
| Agent Logic   | LangChain + LangGraph|
| Web Interface | WebSocket (WS) API   |
| Tool Calling  | LangChain tools      |
| Container     | Docker (multi-stage) |

---

## 📂 Project Structure
```plantext
LLm-inference/
├── .devcontainer/         # Dev environment configs
├── agency/                # Agent tools (calculator, RAG, parser, etc.)
├── data/                  # Persistent data (logs, experiments)
├── llama_cpp_chat_model/  # Llama.cpp wrappers and interfaces
├── models/                # Place your language models here
├── test/                  # Test scripts and utility files
├── utils/                 # Config and logging utilities
├── .env.example           # Template for environment variables
├── main.py                # Main entry point
├── manual_launch.py       # Manual runner example
├── llm_manager.py         # Model manager
├── prompts.py             # Prompt templates
├── websocket.py           # Websocket endpoint server
├── Dockerfile, compose-dev.yaml, devcontainer.json
└── ...
```
---

## ⚙️ Setup

### 📁 Clone the repo

```bash
git clone https://github.com/feed7362/llm-inference.git
cd llm-inference
```
### 🐳 Build & Run via Docker

```bash
docker build -t llm-inference .
docker run --gpus all -p 2222:2222 llm-inference
```

---

### 🧪 WebSocket Usage

Connect to:
```plaintext
ws://localhost:2222/stream
```

Example message payload (JSON):
```json
{
    "messages": "What's the weather in London now?"
}
```

Response format:
```json
{
  "token": {
    "role": "assistant",
    "content": "The weather in London is partly cloudy with a temperature of 20.4°C. The wind is blowing from the southwest at 19.4 km/h, and the relative humidity is 52%. It is daytime.\n"
  }
}
```

---

### 🛠️ Tools (Experimental)

The following tools are integrated (statically or dynamically):
- 🧮 calculator – mathematical expression evaluation
- 🌤️ weather – mock or real-time weather info
- 📚 RAG – retrieval-augmented generation (if vector store is configured)
- 💻 code – code execution (sandboxed)
- 🔍 search – search engine integration (e.g., Google Custom Search API)

> ⚠️ These tools are partially tested and may require stability improvements.

---

### 📈 Future Roadmap
✅ Improve tool testing coverage
- 🔐 Add rate limiting
- 🌍 Add multi-modal support (images, audio)
- 📊 Integrate observability (e.g., Prometheus/Grafana)
- 🔗 Add more LangChain tools
- 🧩 Support more LLMs (e.g., Mistral, Qwen, etc.)
- 🔄 Implement CI/CD with GitHub Actions or GitLab

---

### 🧪 Contributing 
Use the following guidelines for contributions:
- Fork the repo and create a feature branch
- Use devcontainer for development with cuda support
- Document your changes and test tools locally
- Submit a pull request with a clear description of changes

> Note: You can use manual_launch.py to run the server without Docker for local testing.
---

### 📄 License
This project is licensed under the MIT License © 2025.

> Note: The Gemma 3B model is developed and distributed by Google DeepMind under its own license terms. Refer to their official model repository for usage and licensing details.