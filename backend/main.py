import os
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from functools import lru_cache
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from cachetools import TTLCache
from fastapi.middleware.cors import CORSMiddleware


# Load environment variables
from dotenv import load_dotenv
if os.path.exists("secrets.env"):
    load_dotenv("secrets.env")

# Initialize Qdrant Cloud client
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION = "kaustubh_portfolio"

# RAM cache for question embeddings (fast reuse)
embedding_cache = {}
question_vec_cache = TTLCache(maxsize=1000, ttl=60*60*24)  # 24-hour TTL

@lru_cache(maxsize=200)
def embed_via_jina(text: str):
    """Call Jina API to generate embeddings"""
    try:
        res = requests.post(
            "https://api.jina.ai/v1/embeddings",
            headers={
                "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={"model": "jina-embeddings-v3", "input": [text]},
            timeout=10,
        )
        j = res.json()

        if "data" not in j or not j["data"]:
            raise ValueError("No embedding returned from Jina API")

        return j["data"][0]["embedding"]

    except Exception as e:
        raise RuntimeError(f"Embedding API failed: {str(e)}")

def get_question_embedding(q: str):
    """Embed the question and cache it"""
    if q in question_vec_cache:
        return question_vec_cache[q]

    if q in embedding_cache:
        vec = embedding_cache[q]
    else:
        vec = embed_via_jina(q)
        embedding_cache[q] = vec

    question_vec_cache[q] = vec
    return vec

# Initialize FastAPI
app = FastAPI(title="Kaustubh Portfolio Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now (safe since traffic is low and no sensitive exposure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str  # Defines the input JSON schema

@app.get("/ping")
def ping():
    """Health check endpoint"""
    return {"status": "alive"}

@app.post("/chat")
def chat(req: ChatRequest):
    """RAG-grounded chat endpoint"""
    q = req.message.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty message")

    # 1. Embed the question
    try:
        q_vec = get_question_embedding(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Vector search in Qdrant (only verified personal context)
    try:
        res = client.query_points(
        collection_name=COLLECTION,
        query=q_vec,
        limit=5,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="verified",
                    match=MatchValue(value=True),
                )
            ]
        ),
    )
        search_results = res.points
        #context = "\n".join([hit.payload["text"] for hit in search_results]) if search_results else ""
        context = "\n".join(hit.payload.get("text", "") for hit in search_results if hit.payload)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")

    # 3. Strict grounded prompt to reduce hallucination
    prompt = f"""
You are Kaustubh Kasture’s AI portfolio assistant.

IMPORTANT RULE (highest priority):
- Only answer questions that are directly about Kaustubh Kasture or his portfolio.
- If a question is not about him, respond exactly:
  "I’m sorry, I can’t answer that right now. Do you have any other questions about Kaustubh? 😊"

Today’s date: {datetime.now().strftime("%Y-%m-%d")}

TONE:
- Friendly, natural, modern Indian-English
- Smart, crisp, and human sounding (not robotic)
- Avoid unnecessary repetition

RESPONSE RULES:
- Default to **2–3 lines max**
- Give a longer answer **only when the question cannot be answered well in 2–3 lines**
- Keep it factual and grounded to retrieved context
- No sensitive speculation or new personal facts

Context:
{context if context else "No verified context retrieved"}

User Question: {q}

Answer:
"""

    # 4. Call HuggingFace inference API with smaller model (Gemma 2B)
    try:
        llm_res = requests.post(
    "https://router.huggingface.co/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
        "Content-Type": "application/json",
    },
    json={
        "model": "Qwen/Qwen3-4B-Instruct-2507",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.2,
    },
    timeout=30,
)

        if llm_res.status_code != 200:
            raise ValueError(f"LLM API error: {llm_res.status_code} {llm_res.text}")

        data = llm_res.json()
        response_text = data["choices"][0]["message"]["content"].strip()
        return {"response": response_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM inference failed: {str(e)}")
