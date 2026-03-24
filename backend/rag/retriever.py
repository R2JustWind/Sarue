from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from backend.rag.load_docs import load_documents
import logging
import os

logger = logging.getLogger(__name__)

DB_PATH = "faiss_index"

def setup_retriever():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    index_file = os.path.join(DB_PATH, "index.faiss")

    if os.path.exists(index_file):
        db = FAISS.load_local(
            DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        docs = load_documents()

        splitter = CharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=80
        )

        chunks = splitter.split_documents(docs)

        db = FAISS.from_documents(chunks, embedding=embeddings)

        os.makedirs(DB_PATH, exist_ok=True)
        db.save_local(DB_PATH)

    return db.as_retriever(search_kwargs={"k": 5})