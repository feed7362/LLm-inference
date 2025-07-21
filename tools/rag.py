import os
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import Tool
from pydantic import BaseModel
import shutil


class RagInput(BaseModel):
    query: str


def retrieve_context(query: str) -> str:
    """Returns specific knowledge in local database based on a query."""
    urls = [
        "https://docs.python.org/3/tutorial/index.html",
        "https://realpython.com/python-basics/",
        "https://www.learnpython.org/",
    ]
    loader = UnstructuredURLLoader(urls=urls)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50)
    doc_splits = text_splitter.split_documents(docs)

    persist_dir = "../data/chroma"
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)

    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="python_docs",
        embedding=HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5"),
        persist_directory=persist_dir,
    )
    retriever = vectorstore.as_retriever()
    results = retriever.invoke(query)
    return "\n".join([doc.page_content for doc in results])


retrieve_context_tool = Tool(
    name="retrieve_context",
    func=retrieve_context,
    description=(
        "Returns specific knowledge in local database based on a query.\n"
        "Input: { query: string } — e.g., { query: 'list comprehension' }.\n"
        "Output: concatenated text chunks relevant to the query.\n"
    ),
    args_schema=RagInput,
)
