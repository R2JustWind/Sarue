import os
import streamlit as st
import pandas as pd
from langchain_core.documents import Document
import json

@st.cache_data(show_spinner=False)
def load_documents():
    base_dir = os.path.join(os.path.dirname(__file__), "samples")
    paths = ["noticias_ses_1_100.csv", "fiocruz_noticias.csv", "min_saude.csv", "noticias_dodf.csv"]
    dengue_paths = ["dados_dengue-18052026-ano_2025.csv", "dados_dengue-18052026-ano_2026.csv"]

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

    for path in dengue_paths:
        dengue_path = os.path.join(base_dir, path)
        if os.path.exists(dengue_path):
            df_dengue = pd.read_csv(dengue_path, sep=";", engine="python", on_bad_lines="skip", encoding="utf-8")

            for _, row in df_dengue.iterrows():
                classificacao = str(row.get("i_class_final", ""))
                doenca = str(row.get("i_desc_classificacao", ""))
                hospital = str(row.get("i_desc_estab_cnes_notif", ""))
                evolucao = str(row.get("i_desc_evolucao", ""))
                regiao = str(row.get("i_desc_radf_res", ""))
                faixa_etaria = str(row.get("i_faixa_etaria", ""))
                sexo = str(row.get("i_sexo", ""))
                ano = str(row.get("i_ano_prim_sintomas", ""))

                text = f"""
                Registro Epidemológico: {doenca}
                Status do caso: {classificacao}
                Ano dos Primeiros Sintomas: {ano}
                Perfil do Paciente: Sexo {sexo}, Faixa Etária {faixa_etaria}
                Região de Residência (RA): {regiao}
                Local de Notificação (Hospital/Clínica): {hospital}
                Evolução do Caso: {evolucao}
                """

                documents.append(
                    Document(
                        page_content=text.strip(),
                        metadata={
                            "source": path,
                            "tipo": "epidemologia",
                            "doenca": doenca,
                            "classificacao": regiao,
                            "ano": ano
                        }
                    )
                )

    return documents