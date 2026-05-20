from backend.agent import agent_llama, agent
from backend.rag.retriever import setup_retriever
import json

retriever = setup_retriever()

def llama_answer(pergunta):
    docs = retriever.invoke(pergunta)
    
    contexto = "\n\n".join([
        f"Título: {d.metadata.get('titulo')}\n{d.page_content}"
        for d in docs
    ])

    mensagem_com_contexto = f"""
    Você deve usar o contexto abaixo para responder perguntas sobre a Secretaria de Saúde.
    Se a pergunta for sobre localização, UBS ou mapa, use as ferramentas disponíveis.
    Sempre cite a fonte da informação quando possível, especialmente se for uma notícia ou um dado específico de uma UBS.
    Se a informação estiver relacionada a uma notícia, mencione o título da notícia.
    Nunca mencione informações do backend, como nome de funções ou arquivos de onde os dados foram carregados. Foque apenas no conteúdo e na fonte (ex: "notícia do DODF", "dados da UBS X", etc).
    Quando possível, adicione o link para a informação, especialmente se for uma notícia. Se o dado for de uma UBS, mencione o nome da UBS como fonte.
    Se a pergunta envolver quantidade de UBS, lista de UBS ou UBS por região,
    utilize as ferramentas disponíveis para obter os dados mais precisos.

    
    Contexto do DODF:
    {contexto}

    Pergunta do usuário:
    {pergunta}
    """

    result = agent_llama.invoke({
        "messages" : [
            {"type": "human", "content": mensagem_com_contexto}
        ]
    })

    messages = result["messages"]

    response = {
        "type": "chat",
        "action": None,
        "points": [],
        "message": ""
    }

    for msg in messages:
        print("TYPE:", msg.type)
        print("CONTENT:", msg.content)
        if msg.type == "tool":
            try:
                tool_output = json.loads(msg.content)
            except Exception:
                tool_output = None

            if isinstance(tool_output, list) and all("lat" in p for p in tool_output):
                response["type"] = "map_action"
                response["action"] = "add_markers"
                response["points"] = tool_output

            elif tool_output == []:
                response["type"] = "map_action"
                response["action"] = "clear_map"
                response["points"] = []

        if msg.type == "ai":
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                continue

            if msg.content:
                response["message"] = msg.content

    return response["message"]

def qwen_answer(pergunta):
    docs = retriever.invoke(pergunta)
    
    contexto = "\n\n".join([
        f"Título: {d.metadata.get('titulo')}\n{d.page_content}"
        for d in docs
    ])

    mensagem_com_contexto = f"""
    Você deve usar o contexto abaixo para responder perguntas sobre a Secretaria de Saúde.
    Se a pergunta for sobre localização, UBS ou mapa, use as ferramentas disponíveis.
    Sempre cite a fonte da informação quando possível, especialmente se for uma notícia ou um dado específico de uma UBS.
    Se a informação estiver relacionada a uma notícia, mencione o título da notícia.
    Nunca mencione informações do backend, como nome de funções ou arquivos de onde os dados foram carregados. Foque apenas no conteúdo e na fonte (ex: "notícia do DODF", "dados da UBS X", etc).
    Quando possível, adicione o link para a informação, especialmente se for uma notícia. Se o dado for de uma UBS, mencione o nome da UBS como fonte.
    Se a pergunta envolver quantidade de UBS, lista de UBS ou UBS por região,
    utilize as ferramentas disponíveis para obter os dados mais precisos.

    
    Contexto do DODF:
    {contexto}

    Pergunta do usuário:
    {pergunta}
    """

    result = agent.invoke({
        "messages" : [
            {"type": "human", "content": mensagem_com_contexto}
        ]
    })

    messages = result["messages"]

    response = {
        "type": "chat",
        "action": None,
        "points": [],
        "message": ""
    }

    for msg in messages:
        print("TYPE:", msg.type)
        print("CONTENT:", msg.content)
        if msg.type == "tool":
            try:
                tool_output = json.loads(msg.content)
            except Exception:
                tool_output = None

            if isinstance(tool_output, list) and all("lat" in p for p in tool_output):
                response["type"] = "map_action"
                response["action"] = "add_markers"
                response["points"] = tool_output

            elif tool_output == []:
                response["type"] = "map_action"
                response["action"] = "clear_map"
                response["points"] = []

        if msg.type == "ai":
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                continue

            if msg.content:
                response["message"] = msg.content

    return response["message"]