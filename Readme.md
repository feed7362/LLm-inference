docker build -t llama-container .

docker run -it --rm --gpus all llama-container 