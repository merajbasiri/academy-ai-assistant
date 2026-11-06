"""HTTP endpoints and a small browser demo for the academy assistant."""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.agent import MissingAPIKeyError, ask_agent
from app.services import calculate_balance, get_student, get_summary, list_students

PROJECT_ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(
    title="Academy AI Assistant",
    description="A read-only LangChain agent demo using fictional student records.",
    version="1.0.0",
)
app.mount("/assets", StaticFiles(directory=PROJECT_ROOT / "web"), name="assets")


class ChatRequest(BaseModel):
    message: str = Field(min_length=3, max_length=500)


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(PROJECT_ROOT / "web" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/config")
def config():
    """Expose availability, never the API key or model credentials."""
    return {"chat_enabled": bool(os.getenv("OPENAI_API_KEY"))}


@app.get("/summary")
def summary():
    return get_summary()


@app.get("/students")
def students():
    return list_students()


@app.get("/students/{student_id}")
def student_detail(student_id: str):
    student = get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.get("/students/{student_id}/balance")
def student_balance(student_id: str):
    balance = calculate_balance(student_id)
    if balance is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return balance


@app.post("/chat")
def chat(body: ChatRequest):
    try:
        return ask_agent(body.message)
    except MissingAPIKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        # Don't expose upstream messages, stack traces, or credentials to callers.
        raise HTTPException(status_code=502, detail="AI service unavailable") from exc