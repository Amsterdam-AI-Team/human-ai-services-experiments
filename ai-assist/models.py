from pydantic import BaseModel, Field, create_model
from slugify import slugify
from typing import Dict, Any, List


def build_step_model(intent: dict) -> type[BaseModel]:
    # 1. Start with a draft field
    fields = {
        "draft": (
            str,
            Field(
                default="",
                description=(
                    "A running draft of the output document. "
                    "E.g. the objection letter text or address-change request."
                ),
            ),
        )
    }

    # 2. Then one boolean per checklist step
    for step in intent["steps"]:
        key = slugify(step["title"])
        fields[key] = (bool, Field(default=False, description=step["title"]))

    # 3. Finally the follow-up questions
    fields["vragen"] = (
        list[str],
        Field(default_factory=list, description="Dutch follow-up questions"),
    )

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


class IntentMatch(BaseModel):
    """A single intent + similarity pair."""
    intent: Dict[str, Any]
    similarity: float = Field(..., ge=-1.0, le=1.0)


class AnalyzeResponse(BaseModel):
    transcript: str
    matches: List[IntentMatch]