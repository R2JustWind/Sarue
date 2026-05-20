from langchain_core.tools import tool
from backend.utils.load_ubs import load_ubs
import json
from math import sqrt
from typing import Union, List
import unicodedata
import requests
from backend.utils.load_sectors import load_sectors
from backend.utils.ubs_to_gdf import load_ubs_gdf
from shapely.geometry import mapping

UBS_DB = load_ubs()

UBS_GDF = load_ubs_gdf()

SECTORS_GDF = load_sectors()

points = []

cache = {}

def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()

def distance(lat1, lon1, lat2, lon2):
    return sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def geocode_location(query: str):
    global cache

    if query in cache:
        return cache[query]
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{query}, Brasília, DF, Brazil",
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-agent": "Sarue/1.0"
    }

    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        return None

    data = response.json()

    if not data:
        return None
    
    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])

    cache[query] = (lat, lon)

    return lat, lon

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
def clear_sectors():
    """
    Limpa os setores desenhados no mapa.
    Use quando o usuário pedir para limpar, resetar ou remover os setores do mapa.
    """
    return json.dumps({
        "type": "clear_sectors"
    })

@tool
def draw_sector_by_region(region: str, limit: int = 1):
    """
    USE EXCLUSIVAMENTE para desenhar setores censitários do IBGE.

    Esta ferramenta desenha polígonos/malha censitária.

    Utilize SEMPRE quando o usuário mencionar:
    - setor censitário
    - setores censitários
    - malha censitária
    - setor do IBGE
    - polígonos censitários
    - mapa censitário
    - limites censitários

    NÃO utilize esta ferramenta para UBS.

    Exemplos:
    - "me mostre os setores censitários da asa sul"
    - "desenhe a malha censitária do plano piloto"
    - "quero os polígonos censitários da asa norte"
    """

    region = normalize(region)

    filtered = SECTORS_GDF[
        SECTORS_GDF["NM_SUBDIST_NORM"].str.contains(region, case=False, na=False, regex=False)
    ]

    filtered = filtered.head(limit)

    if filtered.empty:
        return json.dumps([])
    
    features = []

    for _, row in filtered.iterrows(): 

        feature = {
            "type": "Feature",
            "properties": {
                "CD_SETOR": row["CD_SETOR"],
                "NM_SUBDIST": row["NM_SUBDIST"]
            },
            "geometry": mapping(row.geometry)
        }

        features.append(feature)

    return json.dumps({
        "response_type": "map_geojson",
        "geojson": {
            "type": "FeatureCollection",
            "features": features
    }
})

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
def find_nearby_ubs_by_location(local: str, limit: Union[int, str] = 5):
    """
    A função retorna uma lista de UBS próximas a uma localização geográfica mencionada pelo usuário.

    Use quando o usuário solicitar a localização de UBS mencionando algum local específico (bairro, ponto de referência, endereço, etc) e pedir para mostrar as UBS próximas àquele local.
    """

    global points

    coords = geocode_location(local)

    if not coords:
        return json.dumps([])
    
    ref_lat, ref_lng = coords

    try:
        limit = int(limit)
    except Exception:
        limit = 5

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
def find_interest_place(query: str):
    """"
    A função retorna um ponto de interesse geocodificado a partir de uma consulta textual.
    Use essa tool quando o usuário pedir para buscar algum ponto de interesse que não seja uma UBS, como um posto de saúde, hospital, ou outro serviço relacionado à saúde.
    """

    coords = geocode_location(query)
    
    if not coords:
        return json.dumps({})
    
    lat, lng = coords

    return json.dumps({
        "lat": lat,
        "lng": lng,
        "label": query,
        "obs": "",
        "endereco": ""
    })

@tool 
def find_nearby_ubs(limit: Union[int, str] = 5):
    """
    A função retorna uma lista de UBS próximas a uma coordenada geográfica.
    Use quando o usuário solicitar postos de saúde, UBS ou serviços próximos de onde ele se encontra.

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

print("TOOLS FILE LOADED")
print("SECTORS:", SECTORS_GDF.shape)