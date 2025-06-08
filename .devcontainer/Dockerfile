# Build stage
FROM nvidia/cuda:12.8.0-devel-ubuntu22.04 AS builder

WORKDIR /app

ENV CUDA_DOCKER_ARCH=all
ENV GGML_CUDA=1

RUN apt update \
    && apt install -y python3-pip cmake g++ wget git ninja-build gcc build-essential \
    && apt autoremove -y && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir cmake scikit-build setuptools

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir cmake scikit-build setuptools
    
#RUN CMAKE_ARGS="-DGGML_CUDA=on" pip install --no-cache-dir llama-cpp-python
RUN CMAKE_ARGS="-DLLAMA_CUDA=on" pip install --no-cache-dir git+https://github.com/abetlen/llama-cpp-python.git

RUN mkdir -p /llama-cpp/site-packages \
    && cp -r /usr/local/lib/python3*/dist-packages/* /llama-cpp/site-packages/ 
    
# Runtime stage
FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip git \
    && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
    fastapi uvicorn[standard] sse-starlette \
    pydantic-settings starlette-context huggingface-hub \
    langchain-openai langchain_huggingface langgraph langchain_community \
    chromadb unstructured

COPY --from=builder /llama-cpp/site-packages /usr/local/lib/python3.10/dist-packages/

COPY . .

EXPOSE 2222

CMD ["python3", "-m", "uvicorn", "main:model_app", "--host", "0.0.0.0", "--port", "2222", "--workers", "4", "--log-level", "debug"]