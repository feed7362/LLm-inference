from llama_cpp import Llama
# installing the package
# llm = Llama.from_pretrained(
#     repo_id="unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
#     filename="DeepSeek-R1-Distill-Qwen-1.5B-Q5_K_M.gguf",
# )   


model = Llama(model_path="models/nlp/DeepSeek-R1-Distill-Qwen-1.5B-Q5_K_M.gguf")
response = model("Tell me a joke", max_tokens=500)
print(response["choices"][0]["text"])