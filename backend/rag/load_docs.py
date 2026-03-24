import os
import streamlit as st
import pandas as pd
from langchain_core.documents import Document
import json

@st.cache_data(show_spinner=False)
def load_documents():
    base_dir = os.path.join(os.path.dirname(__file__), "samples")
    paths = ["noticias_ses_1_100.csv", "fiocruz_noticias.csv", "min_saude.csv", "noticias_dodf.csv"]

    documents = []

    for path in paths:
        df = pd.read_csv(os.path.join(base_dir, path),sep=",",engine="python",on_bad_lines="skip",encoding="utf-8")
        st.write(df.columns)

        for _, row in df.iterrows():
            titulo = str(row.get("title", "")).strip()
            noticia = str(row.get("content", "")).strip()

            text = f"{titulo}\n\n{noticia}".strip()

            if len(text) > 50:
                documents.append(
                    Document(
                        page_content=text,
                        metadata={"source": path}
                    )
                )

    ubs_path = os.path.join(base_dir, "ubs.json")
    if os.path.exists(ubs_path):
        with open(ubs_path, "r", encoding="utf-8") as f:
            ubs_data = json.load(f)

            for ubs in ubs_data:
                nome = ubs.get("nome", "")
                endereco = ubs.get("endereco", "")
                lat = ubs.get("latitude", "")
                lng = ubs.get("longitude", "")

                text = f"""
                Unidade Básica de Saúde: {nome}
                Endereço: {endereco}
                Latitude: {lat}
                Longitude: {lng}
                """

                documents.append(
                    Document(
                        page_content=text.strip(),
                        metadata={
                            "source": "ubs",
                            "tipo": "ubs",
                            "nome": nome,
                            "endereco": endereco,
                            "lat": lat,
                            "lng": lng
                        }
                    )
                )


    return documents