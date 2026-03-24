from langchain_core.tools import tool
from backend.utils.load_ubs import load_ubs
import json
from math import sqrt
from typing import Union, List
import unicodedata

UBS_DB = load_ubs()

points = []

def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()

def distance(lat1, lon1, lat2, lon2):
    return sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

@tool
def remove_ubs_by_name(nome: str):
    """
    Remove uma UBS do mapa pelo nome.
    Use quando o usuário pedir para remover uma UBS específica.
    """
    global points

    nome = nome.lower().strip()

    points = [
        p for p in points
        if nome not in p["label"].lower()
    ]

    return json.dumps(points)

@tool
def add_ubs_by_name(nome: str):
    """"
    A função retorna um ponto ou lista de pontos que corresponde ao ponto da UBS cujo nome foi passada pelo parâmetro.
    Utilize quando o usuário pedir para adicionar uma UBS no mapa pelo nome ou adicionar uma ubs específica no mapa. 

    :param nome: Nome da UBS a ser adicionada ao mapa 
    :type nome: str
    """
    global points

    for ubs in UBS_DB:
        if nome.lower() in ubs["nome"].lower():

            # evitar duplicar
            if not any(p["label"] == ubs["nome"] for p in points):
                points.append({
                    "lat": ubs["lat"],
                    "lng": ubs["lng"],
                    "label": ubs["nome"],
                    "obs": "",
                    "endereco": ubs.get("endereco", "")
                })

            return json.dumps(points)

    return json.dumps([])

@tool 
def find_nearby_ubs(limit: Union[int, str] = 5):
    """
    A função retorna uma lista de UBS próximas a uma coordenada geográfica.
    Use quando o usuário solicitar postos de saúde, UBS ou serviços próximos de uma localidade.

    :param limit: Quantidade de máxima de marcações que podem ser feitas a cada chamada
    :type limit: int
    """
    global points

    try:
        limit = int(limit)
    except Exception:
        limit = 5

    ref_lat = -15.79
    ref_lng = -47.89

    sorted_ubs = sorted(
        UBS_DB,
        key=lambda u: distance(ref_lat, ref_lng, u["lat"], u["lng"])
    )

    selected = sorted_ubs[:limit]

    old_points_by_label = {p["label"]: p for p in points}

    updated_points = []

    for ubs in selected:
        label = ubs["nome"]
        obs = ""

        if label in old_points_by_label:
            obs = old_points_by_label[label].get("obs", "")

        updated_points.append({
            "lat": ubs["lat"],
            "lng": ubs["lng"],
            "label": label,
            "obs": obs,
            "endereco": ubs.get("endereco", "")
        })

    points = updated_points

    return json.dumps(points)

@tool 
def clear_map():
    """
    Limpa todas a marcações atualmente exibidas no mapa.
    Use quando o usuário pedir para limpar, resetar ou remover os pontos do mapa.
    """
    global points
    points = []


    return json.dumps([])

@tool
def add_observation(label: str, obs: str):
    """
    Adiciona ou atualiza uma observação em um ponto do mapa.
    Use quando o usuário pedir para adicionar uma observação em uma UBS.
    """
    global points

    for p in points:
        if label.lower() in p["label"].lower():
            p["obs"] = obs

    return json.dumps(points)


@tool
def find_ubs_by_region(region: str):
    """
    Retorna uma lista de UBS localizadas em uma região específica.
    Use quando o usuário mencionar um bairro ou região e pedir para mostrar as UBS daquela região.
    """
    global points

    if not region:
        return json.dumps([])

    region = normalize(region)

    filtered = [
        ubs for ubs in UBS_DB
        if region in normalize(ubs["nome"])
        or region in normalize(ubs.get("endereco", ""))
    ]

    old_points_by_label = {p["label"]: p for p in points}
    updated_points = []

    for ubs in filtered:
        label = ubs["nome"]
        obs = old_points_by_label.get(label, {}).get("obs", "")

        updated_points.append({
            "lat": ubs["lat"],
            "lng": ubs["lng"],
            "label": label,
            "obs": obs,
            "endereco": ubs.get("endereco", "")
        })

    points = updated_points

    return json.dumps(points)

@tool
def query_ubs_by_region(region: str):
    """
    Retorna dados estruturados sobre UBS de uma região.
    Use para perguntas como:
    - Quantas UBS existem?
    - Quais são as UBS?
    """

    region = normalize(region)

    filtered = [
        ubs for ubs in UBS_DB
        if region in normalize(ubs["nome"])
        or region in normalize(ubs.get("endereco", ""))
    ]

    return json.dumps({
        "count": len(filtered),
        "ubs": [u["nome"] for u in filtered]
    })