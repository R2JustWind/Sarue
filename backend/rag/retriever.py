import os
import json
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def flatten_ses(json_data):
    documentos = []

    try:
        secoes = json_data["diario"]["json"]["INFO"]
    except KeyError:
        print("Estrutura inesperada no JSON.")
        return []

    for nome_secao, secao in secoes.items():

        # verifica se SES existe nessa seção
        ses = secao.get("Secretaria de Estado de Saúde")
        if not ses:
            continue

        docs = ses.get("documentos", {})

        for doc_id, doc in docs.items():
            titulo = doc.get("titulo", "")
            preambulo = doc.get("preambulo", "")
            texto = doc.get("texto", "")

            conteudo = f"""
            TÍTULO: {titulo}

            PREÂMBULO:
            {preambulo}

            TEXTO:
            {texto}
            """.strip()

            if conteudo:
                documentos.append(
                    Document(
                        page_content=conteudo,
                        metadata={
                            "titulo": titulo,
                            "id": doc_id.strip(),
                            "secao": nome_secao
                        }
                    )
                )

    return documentos
    


def load_documents(folder="backend/rag/source"):
    docs = []

    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            path = os.path.join(folder, filename)

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            text = data.get("texto", "")
            title = data.get("texto", filename)

            docs.append(
                Document(
                    page_content=text,
                    metadata={"titulo": title}
                )
            )

    return docs

def create_retriever():
    docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    split_docs = splitter.split_documents(docs)

    embeddings = HuggingFaceBgeEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    db = FAISS.from_documents(split_docs, embeddings)

    return db.as_retriever(search_kwargs={"k": 4})

retriever = create_retriever()