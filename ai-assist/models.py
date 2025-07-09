from pydantic import BaseModel, Field, create_model
from slugify import slugify
from typing import Dict, Any

def build_step_model(intent: dict) -> type[BaseModel]:
    """Create a Pydantic class with one bool per step title."""
    fields = {
        slugify(s["title"]): (bool, Field(default=False, description=s["title"]))
        for s in intent["steps"]
    }
    fields["vragen"] = (list[str], Field(default_factory=list,
                       description="Dutch follow-up questions"))
    return create_model(f"{intent['intentcode']}Model", **fields)


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    intentcode: str
    history: list[dict] | None = None   # optional: full chat as fallback

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    checklist: dict
    finished: bool

class AnalyzeResponse(BaseModel):
    transcript: str
    match: Dict[str, Any]
    similarity: float