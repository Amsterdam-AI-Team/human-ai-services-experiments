from pydantic import BaseModel, Field, create_model
from slugify import slugify
from typing import Dict, Any, List, Optional, Literal


# --------------------------------------------------------------
# Scenario 1: Een laag over interactie
# --------------------------------------------------------------


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


# --------------------------------------------------------------
# Scenario 2: Agent flow
# --------------------------------------------------------------

class YapAccumRequest(BaseModel):
    """Used only when calling /yap with JSON (no file)."""
    text: str = Field("", description="Existing accumulated text (optional)")
    append: str = Field("", description="Text to append")


class YapAccumResponse(BaseModel):
    text: str = Field(..., description="Full accumulated transcript after append")


class YapStartRequest(BaseModel):
    text: str = Field(..., description="Full accumulated transcript to seed the session")
    intentcode: Optional[str] = Field(None, description="Optional intent/workflow tag")


class YapStartResponse(BaseModel):
    yap_session_id: str
    messages: List[Dict[str, Any]]  # [{speaker, message}]
    finished: bool = False
    draft: Optional[str] = None


class YapNextResponse(BaseModel):
    yap_session_id: str
    messages: List[Dict[str, Any]]  # full running chat
    speaker: Literal["burger", "gemeente"]
    message: str
    finished: bool
    draft: Optional[str] = None
