from langchain.agents import create_agent
from backend.tools import find_nearby_ubs, clear_map, add_observation, add_ubs_by_name, remove_ubs_by_name, find_ubs_by_region, query_ubs_by_region
from backend.llm import llm

tools = [find_nearby_ubs, clear_map, add_observation, add_ubs_by_name, remove_ubs_by_name, find_ubs_by_region, query_ubs_by_region]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=""" 
    Você é um assistente especializado em saúde pública e UBS no Brasil.
    Você interage com um mapa que exibe unidades de saúde.

    Contexto:
    A localização atual do usuário é:
    Latitude: -23.55052
    Longitude: -46.633308

    Use ferramentas sempre que precisar alterar o mapa ou buscar dados estruturados.
    Nunca explique que está usando ferramenta.
    Responda normalmente quando não precisar de ferramenta.
    """
)