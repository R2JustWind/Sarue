import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UBS_FILE = BASE_DIR/ "rag" /  "samples" / "ubs.json"

def load_ubs():
    with open(UBS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    normalized = []
    for u in data:
        normalized.append({
            "nome": u["nome"],
            "lat": u["latitude"],
            "lng": u["longitude"],
            "endereco": u.get("endereco", "")
        })

    return normalized