from langchain.agents import create_agent
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.output_parsers import BaseOutputParser
from backend.tools import find_nearby_ubs_by_location, find_nearby_ubs, clear_map, add_observation, add_ubs_by_name, remove_ubs_by_name, find_ubs_by_region, query_ubs_by_region
from backend.tools import find_interest_place, draw_sector_by_region, clear_sectors
from backend.llm import llm, llm_llama

tools = [clear_sectors, draw_sector_by_region, find_nearby_ubs, clear_map, add_observation, add_ubs_by_name, remove_ubs_by_name, find_ubs_by_region, query_ubs_by_region, find_nearby_ubs_by_location, find_interest_place]

print([t.name for t in tools])

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=""" 
    Você é um assistente especializado em saúde pública, UBS e setores censitários no Brasil.
    Você interage com um mapa que exibe UBS e setores censitários.

    IMPORTANTE:
    - Quando o usuário pedir setores censitários de uma região,
    use a ferramenta draw_sector_by_region.
    - Quando o usuário pedir UBS de uma região,
    use find_ubs_by_region.
    - Nunca confunda setores censitários com UBS.

    Contexto:
    A localização atual do usuário é:
    Latitude: -23.55052
    Longitude: -46.633308

    Use ferramentas sempre que precisar alterar o mapa ou buscar dados estruturados.
    Nunca explique que está usando ferramenta.
    Responda normalmente quando não precisar de ferramenta.
    """
)

agent_llama = create_agent(
    model=llm_llama,
    tools=tools,
    system_prompt=""" 
    Você é um assistente especializado em saúde pública, UBS e setores censitários no Brasil.
    Você interage com um mapa que exibe UBS e setores censitários.

    IMPORTANTE:
    - Quando o usuário pedir setores censitários de uma região,
    use a ferramenta draw_sector_by_region.
    - Quando o usuário pedir UBS de uma região,
    use find_ubs_by_region.
    - Nunca confunda setores censitários com UBS.

    Contexto:
    A localização atual do usuário é:
    Latitude: -23.55052
    Longitude: -46.633308

    Use ferramentas sempre que precisar alterar o mapa ou buscar dados estruturados.
    Nunca explique que está usando ferramenta.
    Responda normalmente quando não precisar de ferramenta.
    """
)