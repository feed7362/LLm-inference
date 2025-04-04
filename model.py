from llama_cpp import Llama

model = Llama(model_path="models/nlp/Mahou-1.5-Qwen2.5-1.5B.Q4_K_S.gguf",
            n_gpu_layers=30,
            n_threads=8,
            n_batch=512,
            use_mlock=True,
            use_mmap=True,
            n_ctx=2048,
            )