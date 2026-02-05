from langchain_core.tools import tool
from backend.rag.retriever import retriever
import json

@tool 
def find_nearby_ubs(limit: int = 5):
    """
    A função retorna uma lista de UBS próximas a uma coordenada geográfica.
    Use quando o usuário solicitar postos de saúde, UBS ou serviços próximos de uma localidade.

    :param limit: Quantidade de máxima de marcações que podem ser feitas a cada chamada
    :type limit: int
    """

    lat = -23.55052
    lng = -46.633308

    points = [
        {"lat": lat + 0.001, "lng": lng + 0.001, "label": "UBS Central"},
        {"lat": lat - 0.001, "lng": lng - 0.001, "label": "UBS Norte"},
    ][:limit]

    return json.dumps(points)

@tool 
def clear_map():
    """
    Limpa todas a marcações atualmente exibidas no mapa.
    Use quando o usuário pedir para limpar, resetar ou remover os pontos do mapa.
    """
    
    return json.dumps([])

@tool
def search_news(query: str):
    """
    Busca informações a partir das notícias e documentos fornecidos para responder perguntas para o usuário.
    Use quando o usuário perguntar por informações gerais, notícias ou qualquer informação não relacionada a mapas.
    """

    docs = retriever.invoke(query)

    if not docs:
        return "Nenhuma informação encontrada"
    
    contexto = "\n\n".join(
        f"{doc.metadata.get('titulo','')}:\n{doc.pag_content}"
        for doc in docs
    )

    return contexto