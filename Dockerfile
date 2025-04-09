FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

WORKDIR /app

ENV CUDA_DOCKER_ARCH=all
ENV GGML_CUDA=1

RUN apt update \
    && apt upgrade -y \
    && apt install -y python3 python3-pip python3-dev cmake g++ wget git ninja-build gcc build-essential \
    && apt autoremove -y && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
    pytest cmake scikit-build setuptools fastapi uvicorn sse-starlette \
    pydantic-settings starlette-context huggingface-hub notebook jupyter ipywidgets

RUN CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python

COPY . .

EXPOSE 2222

CMD ["python3", "-m", "uvicorn", "main:model_app", "--host", "0.0.0.0", "--port", "2222", "--workers", "4", "--log-level", "debug"]