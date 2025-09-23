from pydantic import BaseModel, Field, create_model
from slugify import slugify
from typing import Dict, Any, List, Optional, Literal
from uuid import UUID

# Import i18n when module is loaded
try:
    from i18n import get_translation, normalize_language_code
except ImportError:
    # Fallback if i18n module not available during initialization
    def get_translation(lang_code: str, key: str, default: str = "") -> str:
        return default
    def normalize_language_code(lang_code: str) -> str:
        return lang_code or "nl"


# --------------------------------------------------------------
# Scenario 1: Een laag over interactie
# --------------------------------------------------------------


def build_step_model(intent: dict, language: str = "nl") -> type[BaseModel]:
    lang_code = normalize_language_code(language)

    # Get localized intent to use for step titles
    from i18n import get_intents
    localized_intents = get_intents(lang_code)
    localized_intent = next(
        (i for i in localized_intents if i["intentcode"] == intent["intentcode"]),
        intent  # fallback to original if not found
    )

    # 1. Start with a draft field
    draft_desc = get_translation(lang_code, "model_descriptions.draft",
                                "A running draft of the output document. E.g. the objection letter text or address-change request.")
    fields = {
        "draft": (
            str,
            Field(
                default="",
                description=draft_desc,
            ),
        )
    }

    # 2. Then one boolean per checklist step - use localized steps
    for step in localized_intent["steps"]:
        key = slugify(step["title"])
        fields[key] = (bool, Field(default=False, description=step["title"]))

    # 3. Finally the follow-up questions
    vragen_desc = get_translation(lang_code, "model_descriptions.vragen", 
                                 f"{language.title()} follow-up questions")
    fields["vragen"] = (
        list[str],
        Field(default_factory=list, description=vragen_desc),
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
    draft: str = Field(default="", description="Werkversie van de samengestelde tekst/bezwaarschrift; mag onvolledig zijn.")
    finished: bool
    user_text: str


class IntentMatch(BaseModel):
    """A single intent + similarity pair."""
    intent: Dict[str, Any]
    similarity: float = Field(..., ge=-1.0, le=1.0)


class AnalyzeResponse(BaseModel):
    transcript: str
    language: str
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
    language: str


class YapStartRequest(BaseModel):
    text: str = Field(..., description="Full accumulated transcript to seed the session")
    intentcode: Optional[str] = Field(None, description="Optional intent/workflow tag")
    language: Optional[str] = Field(None, description="Language code (nl, en, fr)")


class YapStartResponse(BaseModel):
    yap_session_id: str
    messages: List[Dict[str, Any]]  # [{speaker, message}]


class YapNextResponse(BaseModel):
    yap_session_id: str
    messages: List[Dict[str, Any]]  # full running chat
    speaker: Literal["burger", "gemeente"]
    message: str
    finished: bool
    draft: Optional[str] = None


def create_burger_turn_model(language: str = "nl") -> type[BaseModel]:
    """Create BurgerTurn model with localized descriptions."""
    lang_code = normalize_language_code(language)
    message_desc = get_translation(lang_code, "model_descriptions.burger_message", "Antwoord van de burger")
    
    class BurgerTurn(BaseModel):
        """Burger mag alleen antwoorden geven – géén status‑velden."""
        message: str = Field(..., description=message_desc)
    
    return BurgerTurn


def create_gemeente_turn_model(language: str = "nl") -> type[BaseModel]:
    """Create GemeenteTurn model with localized descriptions."""
    lang_code = normalize_language_code(language)
    finished_desc = get_translation(lang_code, "model_descriptions.gemeente_finished", "Akkoord bereikt?")
    message_desc = get_translation(lang_code, "model_descriptions.gemeente_message", "Openstaande vragen (één string, regels gescheiden door \\n)")
    draft_desc = get_translation(lang_code, "model_descriptions.gemeente_draft", "Definitieve samenvatting of concept‑tekst")
    
    class GemeenteTurn(BaseModel):
        """Gemeente beheert de processtatus."""
        finished: bool = Field(False, description=finished_desc)
        message: str = Field(..., description=message_desc)
        draft: Optional[str] = Field(None, description=draft_desc)
    
    return GemeenteTurn


# Backward compatibility - default Dutch models
BurgerTurn = create_burger_turn_model("nl")
GemeenteTurn = create_gemeente_turn_model("nl")


class FeedbackRequest(BaseModel):
    feedback: str
    concept: int | None = None
    language: str | None = None
    session_id: UUID | None = None