from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
import os
import json
from backend import agent

BASE_DIR = Path(__file__).resolve().parent.parent
key = os.getenv("GROQ_API_KEY")
print("KEY REPR:", repr(key))
print("KEY LEN:", len(key) if key else None)

print("GROQ_API_KEY =", os.getenv("GROQ_API_KEY"))

FRONTEND_DIR = BASE_DIR / 'frontend'

app = FastAPI()
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")

class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(request: ChatRequest):
    result = agent.agent.invoke({
        "messages": [{"role": "user", "content": request.message}]
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

        if msg.type == "ai" and msg.content: 
            response["message"] = msg.content

    return response