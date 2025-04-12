docker build -t jb-devcontainer-llama_gpu_devcontainer .

docker run --rm --gpus all -p 2222:2222 jb-devcontainer-llama_gpu_devcontainer