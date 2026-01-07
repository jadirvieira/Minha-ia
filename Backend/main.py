from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

app = FastAPI()

# Permitir acesso do frontend (mesmo em outro domínio)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MEMORY_FILE = "memories.json"

# Carrega ou inicializa memórias
def load_memories():
    if not os.path.exists(MEMORY_FILE):
        return {
            "values": [
                "Seja claro e direto",
                "Não invente fatos",
                "Respeite a privacidade",
                "Peça esclarecimento se não entender"
            ],
            "lessons": []  # lista de {"input": "...", "good_response": "...", "bad_response": "..."}
        }
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memories(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.get("/status")
def status():
    return {"status": "IA em desenvolvimento 🌱"}

@app.get("/personality")
def get_personality():
    mem = load_memories()
    return {
        "values": mem["values"],
        "lesson_count": len(mem["lessons"])
    }

@app.post("/respond")
def respond(query: dict):
    user_input = query.get("text", "").strip()
    mem = load_memories()

    # Regra super simples: se for curto e direto, responda com base em valores
    if "oi" in user_input.lower() or "olá" in user_input.lower():
        response = "Olá! Como posso te ajudar hoje?"
    elif "valores" in user_input.lower():
        response = "Meus valores são:\n• " + "\n• ".join(mem["values"])
    elif "aprendeu" in user_input.lower():
        count = len(mem["lessons"])
        response = f"Já aprendi {count} lições com você. Quer ver alguma?"
    else:
        # Resposta genérica (depois podemos conectar a uma LLM)
        response = f"Entendi: '{user_input}'. Ainda estou aprendendo — posso tentar melhorar?"

    return {"response": response}

@app.post("/feedback")
def feedback(feedback: dict):
    # Exemplo: {"user_input": "...", "response": "...", "is_good": false, "corrected": "..."}
    mem = load_memories()
    lesson = {
        "input": feedback["user_input"],
        "bad_response": feedback["response"],
        "good_response": feedback.get("corrected", ""),
        "is_good": feedback["is_good"]
    }
    mem["lessons"].append(lesson)
    save_memories(mem)
    return {"status": "Lição salva ✅"}
