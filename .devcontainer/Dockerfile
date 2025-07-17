# --- Build llama-cpp with CUDA ---
FROM nvidia/cuda:12.8.0-devel-ubuntu22.04 AS cuda_builder

WORKDIR /app

ENV CUDA_DOCKER_ARCH=all
ENV GGML_CUDA=1

RUN apt update \
    && apt install -y python3-pip cmake g++ wget git ninja-build gcc build-essential \
    && apt autoremove -y && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install cmake scikit-build setuptools
    
RUN CMAKE_ARGS="-DLLAMA_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=75\;86\;89" pip install llama-cpp-python

WORKDIR /whisper
RUN git clone https://github.com/ggerganov/whisper.cpp.git . && \
    sed -i 's/set(BUILD_SHARED_LIBS_DEFAULT ON)/set(BUILD_SHARED_LIBS_DEFAULT OFF)/' CMakeLists.txt && \
    cmake -B build -DGGML_CUDA=1 -DCMAKE_CUDA_ARCHITECTURES=75\;86\;89 . && \
    cmake --build build -j6 --config Release
# Copy the built whisper binary and avoiding the need for .so files

RUN mkdir -p /llama-cpp/site-packages \
    && cp -r /usr/local/lib/python3.*/dist-packages/llama_cpp* /llama-cpp/site-packages/

# --- Runtime stage ---
FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_SYSTEM_PYTHON=1
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y python3-pip git \
    && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY --from=cuda_builder /llama-cpp/site-packages /usr/local/lib/python3.10/dist-packages/
COPY --from=cuda_builder /whisper/build/bin /usr/local/bin/whisper

ENV PATH="/usr/local/bin/whisper:${PATH}"
ENV UV_LINK_MODE=copy 
# Use copy mode for hardlinking

COPY . .

RUN uv pip install -r pyproject.toml

EXPOSE 2222

CMD ["python3", "-m", "uvicorn", "main:model_app", "--host", "0.0.0.0", "--port", "2222", "--workers", "4", "--log-level", "debug"]