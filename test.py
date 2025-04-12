#%%
from llama_cpp import Llama

model = Llama(model_path="models/nlp/Mahou-1.5-Qwen2.5-1.5B.Q4_K_S.gguf",
              n_gpu_layers=30,
              n_threads=8,
              n_batch=512,
              use_mlock=True,
              use_mmap=True,
              n_ctx=4096
              )
#%%
query = "Q: Name the number of planets in the solar system? A: "
response = model(query,
                 stop=["\n", "Q:", "A:", "?", ".", "User:", "Assistant:"],
                 max_tokens=min(len(query.split()) * 3, 512),
                 temperature=0.7,
                 top_p=0.9,
                 top_k=50,
                 stream=True
                 )
for chunk in response:
    print(chunk["choices"][0]["text"], end="")