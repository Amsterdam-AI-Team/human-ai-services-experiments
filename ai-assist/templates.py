import os
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

# Initialize AzureChatOpenAI with custom HTTP clients
llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),  # alias: azure_deployment
    api_version=os.getenv("OPENAI_API_VERSION"),
    temperature=0.4,
    streaming=True,
    http_client=sync_client,
    http_async_client=async_client
)

llm = llm.bind(response_format="json_object")

def make_chain(step_model: type[BaseModel]):
    """
    Bouwt één LangChain-chain die:
      1. Een lijst BaseMessages maakt uit history + nieuwe user-message
      2. De LLM oproept en verwacht JSON-output
      3. Het resultaat in een Pydantic-object parseert
    """
    parser = PydanticOutputParser(pydantic_object=step_model)

    json_parser = JsonOutputParser(pydantic_object=step_model)
    format_instr = json_parser.get_format_instructions()

    system_msg = SystemMessage(
        content=(
            "Je bent een behulpzame jurist van de gemeente. "
            "Stel alleen vragen die nodig zijn om de checklist af te vinken."
            "Antwoord _altijd_ in strikt geldige JSON met dit schema:\n"
            f"{format_instr}\n"
            "Stuur _niets anders_."
        )
    )

    def to_message(d: dict):
        """Zet history- en user dict om in BaseMessage-objecten"""
        role = d.get("role")
        raw = d.get("content", "")
        # if the content is a list (like vragen), take the first question
        if isinstance(raw, list):
            content = raw[0] if raw else ""
        else:
            content = raw
        if role == "user":
            return HumanMessage(content=content)
        elif role == "assistant":
            return AIMessage(content=content)
        else:
            return SystemMessage(content=content)

    async def run_chain(x: dict) -> BaseModel:
        # 1. Bouw de messages-lijst
        messages = [system_msg] + [to_message(m) for m in x.get("history", [])]
        messages.append(HumanMessage(content=x.get("message", "")))
        
        # 2. Roep de LLM aan met agenerate
        llm_response = await llm.agenerate(messages=[messages])
        # agenerate returns LLMResult with .generations: list[list[Generation]]
        text = llm_response.generations[0][0].text
        
        # 3. Parse de JSON-tekst naar Pydantic-model
        return parser.parse(text)

    return run_chain