############################################################
# Builder stage: compile llama-cpp-python & whisper.cpp with CUDA
############################################################
FROM nvidia/cuda:12.8.0-devel-ubuntu22.04 AS cuda_builder

WORKDIR /app

ENV CUDA_DOCKER_ARCH=all
ENV GGML_CUDA=1

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y git build-essential \
    python3 python3-pip gcc wget \
    ocl-icd-opencl-dev opencl-headers clinfo \
    libclblast-dev libopenblas-dev \
    && mkdir -p /etc/OpenCL/vendors && echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/opt/venv/bin:${PATH}" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT="/opt/venv"

COPY pyproject.toml .

RUN uv venv /opt/venv

RUN uv add cmake scikit-build setuptools \
    && CMAKE_ARGS="-DGGML_CUDA=1 -DCMAKE_CUDA_ARCHITECTURES=75;86;89" uv pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir --verbose

RUN uv sync --no-dev

WORKDIR /whisper
RUN git clone https://github.com/ggerganov/whisper.cpp.git . && \
    sed -i 's/set(BUILD_SHARED_LIBS_DEFAULT ON)/set(BUILD_SHARED_LIBS_DEFAULT OFF)/' CMakeLists.txt && \
    cmake -B build -DGGML_CUDA=1 -DCMAKE_CUDA_ARCHITECTURES=75\;86\;89 . && \
    cmake --build build -j7 --config Release
# Copy the built whisper binary and avoiding the need for .so files

############################################################
# Runtime stage
############################################################
FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/opt/venv/bin:${PATH}" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT="/opt/venv"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-pip git libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY . .

COPY --from=cuda_builder /opt/venv /opt/venv
COPY --from=cuda_builder /whisper/build/bin /usr/local/bin/whisper
ENV PATH="/usr/local/bin/whisper:${PATH}"

RUN uv sync --no-dev

EXPOSE 2222

CMD ["python3", "-m", "uvicorn", "main:model_app", "--host", "0.0.0.0", "--port", "2222", "--workers", "4", "--log-level", "debug"]