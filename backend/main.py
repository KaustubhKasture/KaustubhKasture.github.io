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
from sentence_transformers import CrossEncoder


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

#Cross encoder re-ranker for better relevance
#reranker = CrossEncoder('BAAI/bge-reranker-base-v1.5')
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L4-v2")

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

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "qwen/qwen3.8-27b"

def groq_chat(prompt: str, max_tokens: int, temperature: float) -> str:
    """Call Groq chat completions. reasoning_effort none keeps short RAG replies out of thinking tokens."""
    r = requests.post(
        GROQ_CHAT_URL,
        headers={
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "reasoning_effort": "none",
        },
        timeout=30,
    )

    if r.status_code != 200:
        raise ValueError(f"Groq API error: {r.status_code} {r.text}")

    content = r.json()["choices"][0]["message"].get("content")
    if not content or not str(content).strip():
        raise ValueError("Groq returned an empty response")
    return str(content).strip()

def rewrite_query(q: str) -> str:
    """Rewrite the query to focus on Kaustubh portfolio information"""
    prompt = f"""
    Rewrite the following question to focus only on information about Kaustubh Kasture and his portfolio.

    Query: {q}
    Rewritten Query:
    """
    return groq_chat(prompt, max_tokens=40, temperature=0.1)

def qdrant_search(query_text: str, limit: int = 10):
    """Vector Search in Qdrant using rewritten query and filter for verified context only"""
    q_vec = get_question_embedding(query_text)
    res = client.query_points(
        collection_name=COLLECTION,
        query=q_vec,
        limit=limit,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="verified",
                    match=MatchValue(value=True),
                )
            ]
        ),
    )
    return res.points

def rerank_results(query_text: str, points, top_k: int = 5):
    """Rerank Qdrant results using cross-encoder relevance scores"""
    docs = []
    for hit in points:
        payload = hit.payload or {}
        text = payload.get("text", "")
        if text:
            docs.append(text)
    
    if not docs:
        return ""
    
    pairs = [(query_text, doc) for doc in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, docs),reverse = True)
    top_docs = [doc for _, doc in ranked[:top_k]]
    return "\n".join(top_docs)

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
    
    # Rewrite query to focus on Kaustubh portfolio (helps both embedding and LLM relevance)
    try:
        rewritten = rewrite_query(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query rewriting failed: {str(e)}")
    
    # Embed the rewritten query and search in Qdrant for verified context only
    try:
        search_results = qdrant_search(rewritten, limit=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")
    
    # Rerank results with cross-encoder for better relevance    
    try:
        context = rerank_results(rewritten, search_results, top_k=5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reranking failed: {str(e)}")

    # 3. Strict grounded prompt to reduce hallucination
    prompt = f"""
You are Kaustubh Kasture’s AI portfolio assistant.

IMPORTANT RULE (highest priority):
- Only answer questions that are directly about Kaustubh Kasture or his portfolio.
- If a question is not about him, respond exactly:
  "I’m sorry, I can’t answer that right now. Do you have any other questions about Kaustubh?"

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

    # 4. Answer from retrieved context with Groq-hosted Qwen 3.8 27B
    try:
        response_text = groq_chat(prompt, max_tokens=200, temperature=0.2)
        return {"response": response_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM inference failed: {str(e)}")
