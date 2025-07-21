import os
import json
import httpx
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from models import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

import socket

# ── Workaround for WSL DNS issues: force host resolution to the public IP ──
PUBLIC_IP = "100.64.1.20"  # replace with your resource's actual public front-door IP
TARGET_HOST = "ai-openai-ont.openai.azure.com"

# Save the original for fallback
_orig_getaddrinfo = socket.getaddrinfo


def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    # Redirect DNS lookups for TARGET_HOST to PUBLIC_IP
    if host == TARGET_HOST:
        host = PUBLIC_IP
    return _orig_getaddrinfo(host, port, family, type, proto, flags)


# Apply monkey-patch globally before any HTTPX calls
socket.getaddrinfo = custom_getaddrinfo

# Create HTTPX clients (no special transport needed now)
sync_client = httpx.Client()
async_client = httpx.AsyncClient()

# Initialize AzureChatOpenAI with proxied clients
llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    temperature=0.4,
    streaming=False,
    http_client=sync_client,
    http_async_client=async_client
)

llm = llm.bind(response_format="json_object")


# Updated: make_chain now takes session dict so it can persist state (e.g. draft)
def make_chain(step_model: type[BaseModel], session: dict):
    """
    Bouwt één LangChain-chain die:
      1. De JSON-schema instructies infereren van het Pydantic-model
      2. Een systeem prompt maakt dat alleen strikt die JSON mag outputten
      3. De LLM oproept en de JSON parseert naar het Pydantic-model
      4. De draft persist in session
    """
    parser = PydanticOutputParser(pydantic_object=step_model)
    json_parser = JsonOutputParser(pydantic_object=step_model)
    format_instr = json_parser.get_format_instructions()

    system_msg = SystemMessage(
        content=(
            "Je bent een behulpzame jurist van de gemeente."

            "Antwoord _altijd_ in strikt geldige JSON met dit schema:"

            f"{format_instr}"

            "- `draft`: de volledige bijgewerkte concepttekst."

            "- Als je meer informatie nodig hebt voor een stap die nog `false` is, laat die boolean staan en zet je vraag in de `vragen` array."

            "Stuur _alleen_ de JSON-object."
        )
    )

    def to_message(d: dict):
        """Zet history- en user dict om in BaseMessage-objecten"""
        role = d.get("role")
        raw = d.get("content", "")
        # if the content is a list (zoals vragen), neem de eerste string
        content = raw[0] if isinstance(raw, list) and raw else raw
        if role == "user":
            return HumanMessage(content=content)
        elif role == "assistant":
            return AIMessage(content=content)
        else:
            return system_msg

    async def run_chain(x: dict) -> BaseModel:
        # 1. System prompt + prior draft context
        messages = [system_msg]
        # Include previous JSON state (booleans + draft) so model sees existing values
        prev_draft = session.get("draft", "")
        prev_flags = json.dumps({
            **{k: v for k, v in session.get("checklist", {}).items()},
            "draft": prev_draft
        })
        if session.get("checklist"):
            messages.append(AIMessage(content=prev_flags))
        # 2. re-build entire history
        messages += [to_message(m) for m in x.get("history", [])]
        # 3. current user message
        messages.append(HumanMessage(content=x.get("message", "")))

        # 4. call LLM
        result = await llm.agenerate(messages=[messages])
        text = result.generations[0][0].text

        # 5. parse JSON into model
        step_obj = parser.parse(text)

        # 6. persist new draft
        session["draft"] = step_obj.draft
        return step_obj

    return run_chain


# Hergebruik dezelfde LLM-config als elders (of maak aparte instanties).
_yap_llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    temperature=0.4,
)

BURGER_SYSTEM = (
    "Je bent een inwoner van de gemeente die een subsidie voor een buurtfeest wil aanvragen. "
    "Je reageert bondig, in spreektaal. Gebruik de informatie in de transcriptie als basis. "
    "Voeg relevante details toe als die ontbreken."
)

GEMEENTE_SYSTEM = (
    "Je bent een medewerker van de gemeente die subsidieaanvragen beoordeelt. "
    "Stel gerichte vragen (budget, datum, aantal deelnemers, toegankelijkheid, duurzaamheid). "
    "Werk toe naar een kort akkoord met subsidiebedrag en voorwaarden. "
    "Als alle informatie compleet is, zeg dat we akkoord zijn en vat samen in 1 alinea."
)


async def _yap_generate(role: str, transcript: str, history: list[dict]) -> str:
    """
    Laat 'burger' of 'gemeente' spreken, gegeven de transcript seed en tot nu toe bekende messages.
    history: list[{speaker, message}] in chronologische volgorde.
    Retourneert de nieuwe utterance (str).
    """
    if role == "burger":
        sys_msg = SystemMessage(content=BURGER_SYSTEM + f"\n\nTranscript basis:\n{transcript}")
    else:
        sys_msg = SystemMessage(content=GEMEENTE_SYSTEM)

    msgs = [sys_msg]
    for turn in history:
        speaker = turn["speaker"]
        text = turn["message"]
        if speaker == "burger":
            msgs.append(HumanMessage(content=text))
        else:  # gemeente
            msgs.append(AIMessage(content=text))

    # De model-uitspraak: we behandelen altijd de volgende beurt als AIMessage
    # omdat we de rol mapping in history zelf bijhouden.
    resp = await _yap_llm.apredict_messages(msgs)
    # apredict_messages() geeft een BaseMessage terug; pak content
    return resp.content if hasattr(resp, "content") else str(resp)


def _yap_check_finished(history: list[dict]) -> tuple[bool, str | None]:
    """
    Heuristiek: als de laatste gemeente-bericht woorden bevat als 'akkoord' OF 'subsidie'
    en 'samenvatting' of 'hier is het concept', dan beschouwen we het gesprek als afgerond
    en genereren we een draft uit de laatste gemeente-uitspraak.
    """
    if not history:
        return False, None
    last = history[-1]
    if last["speaker"] != "gemeente":
        return False, None

    text = last["message"].lower()
    if any(w in text for w in ("akkoord", "goedgekeurd", "subsidie toegekend")):
        # draft = laatste gemeente-uitspraak; in praktijk kun je hier nog
        # een aparte 'maak samenvatting' call doen.
        draft = history[-1]["message"]
        return True, draft
    return False, None
