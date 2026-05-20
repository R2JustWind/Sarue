from langchain_ollama import ChatOllama
import os

llm = ChatOllama(
    model="qwen3.5:9b",
    temperature=0.3
)

llm_llama = ChatOllama(
    model="llama3.1:8b",
    temperature=0.3
)