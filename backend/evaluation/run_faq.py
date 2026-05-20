import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(ROOT_DIR)

import json
from respostas import llama_answer, qwen_answer

with open("dataset_qa_dodf.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

resultados = []

for item in dataset:
    pergunta = item["pergunta"]

    resposta_llama = llama_answer(pergunta)
    #resposta_qwen = qwen_answer(pergunta)

    resultados.append({
        "pergunta": pergunta,
        "resposta_llama": resposta_llama or "Sem resposta",
        #"resposta_qwen": resposta_qwen,
        "resposta_ref": item["resposta"],
        "secao": item.get("secao"),
        "fonte": item.get("fonte"),
    })

with open("resultados_llama.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)