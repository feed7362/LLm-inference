from typing import Any

import chromadb
from chromadb import QueryResult
from sentence_transformers import SentenceTransformer
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

from utils.logger import CustomLogger
logger = CustomLogger(__name__)

client = chromadb.PersistentClient(
    path="./data/chroma",
)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

queries_cache = client.get_or_create_collection(
    name="queries_cache",
    metadata={"type": "cache"}
)

executor = ThreadPoolExecutor()


async def async_embed(query: str) -> list[float]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, lambda: embedder.encode(query).tolist())


async def async_chroma_query(query_vec: list[float]) -> QueryResult:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, lambda: queries_cache.query(query_embeddings=[query_vec], n_results=1))


async def async_chroma_add(id_: str, embedding: list[float], doc:  str | list[str] | None, meta: dict):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, lambda: queries_cache.add(
        ids=[id_], embeddings=[embedding], documents=[doc], metadatas=[meta]
    ))


async def search_with_semantic_cache(query: Any) -> Any | None:
    query_vec = await async_embed(query)
    results = await async_chroma_query(query_vec)
    logger.info("Retrieved results from cache: %s", results)

    docs = results.get("documents", [])
    distances = results.get("distances", [])

    if docs and docs[0] and distances and distances[0] and distances[0][0] < 0.15:
        return docs[0][0]
    return None



async def generate_new_result(query: str, new_result:  str | list[str] | None) -> None:
    query_vec = await async_embed(query)
    logger.info("New query vector generated: %s", query_vec)
    await async_chroma_add(str(uuid.uuid4()), query_vec, new_result, {"query": query})
