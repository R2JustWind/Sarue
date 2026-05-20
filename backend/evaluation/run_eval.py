import json
from avaliacao import avaliar_dataset
from score import media_modelo
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(ROOT_DIR)

with open("dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

resultados = avaliar_dataset(dataset)

with open("resultados.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print("Avaliação concluída e salva em resultados.json")

media_llama = media_modelo(resultados, "avaliacao_llama")
media_qwen = media_modelo(resultados, "avaliacao_qwen")

print("\nMÉDIA LLaMA:")
print(media_llama)

print("\nMÉDIA Qwen:")
print(media_qwen)