from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List

app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDMyNjRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.049Szuxt3TGZ83SEJLY0dEIppr6uYmyjJzj9Dvd_EMg"

class Link(BaseModel):
    url: str
    text: str

class AnswerResponse(BaseModel):
    answer: str
    links: List[Link]

KNOWLEDGE_BASE = {
    "gpt-3.5-turbo-0125": {
        "answer": "You should use gpt-4o-mini as it's the supported model in the AI proxy provided for this course.",
        "links": [
            {"url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939", "text": "Model Discussion"}
        ]
    },
    "dashboard": {
        "answer": "A score of 10/10 plus bonus would appear as 110 on the dashboard.",
        "links": [
            {"url": "https://discourse.onlinedegree.iitm.ac.in/t/ga4-data-sourcing-discussion-thread-tds-jan-2025/165959/388", "text": "Grading Policy"}
        ]
    },
    "docker": {
        "answer": "While Docker is acceptable, we recommend using Podman for this course.",
        "links": [
            {"url": "https://tds.s-anand.net/#/docker", "text": "Container Guidelines"}
        ]
    }
}

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True

@app.post("/", response_model=AnswerResponse)
async def answer_question(request: Request, auth: bool = Depends(verify_token)):
    data = await request.json()
    question = data.get("question", "").lower()

    for keyword, response in KNOWLEDGE_BASE.items():
        if keyword in question:
            return response

    return {
        "answer": "I couldn't find an answer. Try asking about: " + ", ".join(KNOWLEDGE_BASE.keys()),
        "links": []
    }
import logging

logger = logging.getLogger("uvicorn.error")

@app.post("/")
async def answer_question(request: Request, auth: bool = Depends(verify_token)):
    try:
        data = await request.json()
        # your existing logic here, e.g.,
        question = data.get("question", "").lower()

        for keyword, response in KNOWLEDGE_BASE.items():
            if keyword in question:
                return response

        return {
            "answer": "I couldn't find an answer. Try asking about: " + ", ".join(KNOWLEDGE_BASE.keys()),
            "links": []
        }
    except Exception as e:
        logger.error(f"Error in / endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# 👇👇 This is crucial for Vercel
# Export as `app` so Vercel sees it
handler = app
