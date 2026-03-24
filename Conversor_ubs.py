import pandas as pd
import json

arquivo = "Unidades_Basicas_Saude-UBS.csv"

df = pd.read_csv(
    arquivo,
    sep=";",
    quotechar='"',
    encoding="latin1"
)

df_df = df[df["UF"] == 53].copy()

df_df = df_df.dropna(subset=["LATITUDE", "LONGITUDE"])

df_df = df_df[df_df["NOME"].str.startswith("UBS")]

palavras_excluir = ["PDF", "CPP", "CDP", "CONSULTORIO"]

for palavra in palavras_excluir:
    df_df = df_df[~df_df["NOME"].str.upper().str.contains(palavra)]

df_df = df_df.drop_duplicates(subset=["NOME"])

df_df["LATITUDE"] = (
    df_df["LATITUDE"]
    .astype(str)
    .str.replace(",", ".")
    .astype(float)
)

df_df["LONGITUDE"] = (
    df_df["LONGITUDE"]
    .astype(str)
    .str.replace(",", ".")
    .astype(float)
)

resultado = []

for i, (_, row) in enumerate(df_df.iterrows(), start=1):
    resultado.append({
        "id": i,
        "nome": row["NOME"],
        "latitude": row["LATITUDE"],
        "longitude": row["LONGITUDE"],
        "endereco": row["LOGRADOURO"]
    })

with open("ubs.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=4)
