from langchain.agents import create_agent
from backend.tools import find_nearby_ubs, clear_map
from backend.llm import llm

tools = [find_nearby_ubs, clear_map]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="Você é um assistente útil e preciso, com foco em saúde pública e serviços públicos brasileiros que interage com um mapa.\n" 
    "A localização atual do usuário é: \n"
    "Latitude: -23.55052, Longitude: -46.633308\n"
    "Sempre que o usuário pedir para ver UBS próximas, utilize a ferramenta find_nearby_ubs."
    "Use informações fornecidas pelas ferramentas sempre que disponíveis."
    "Se não houver informação suficiente, responda normalmente."
)