import os
import json
import httpx
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from models import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
import socket
from models import GemeenteTurn, BurgerTurn
from langchain.output_parsers import OutputFixingParser


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

llm = llm.bind(response_format="json_object", temperature=0)


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

    # Get localized system prompt
    lang_code = normalize_language_code(language)
    prompt_data = get_system_prompt(lang_code, "juridisch_medewerker")
    language_suffix = get_language_suffix(lang_code)

    system_content = f"""
                        {prompt_data['role']}

                        {prompt_data['instructions']}
                        {format_instr}

                        {prompt_data['workflow']}

                        {prompt_data['important']}
                        - {language_suffix}
                    """

    system_msg = SystemMessage(content=system_content)

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

        # Include previous JSON state (separate top-level keys for checklist and draft)
        prev_state = {"checklist": session.get("checklist", {}), "draft": session.get("draft", "")}
        prev_flags = json.dumps(prev_state, ensure_ascii=False)
        if session.get("checklist") or session.get("draft"):
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


yap_llm_gemeente = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    temperature=0.4,
).bind(response_format={"type": "json_object"})

yap_llm_burger = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    temperature=0.4,
).bind(response_format={"type": "json_object"})



def build_burger_system_prompt(transcript: str, schema: str, format: str, language: str = "nl") -> str:
    """Build localized BURGER_SYSTEM prompt."""
    lang_code = normalize_language_code(language)
    prompt_data = get_system_prompt(lang_code, "burger_system")
    language_suffix = get_language_suffix(lang_code)

    # Get localized text for JSON instruction
    from i18n import get_translation
    json_instruction = get_translation(lang_code, "system_prompts.juridisch_medewerker.instructions",
                                       "Geef ALTIJD strikt geldige JSON volgens dit schema:")
    transcript_label = get_translation(
        lang_code, "labels.transcript", "Transcript (door de gebruiker aangeleverd):")

    return f"""
                <Context>
                {prompt_data['context']}
                {transcript_label}
                {transcript}
                </Context>

                <Objective>
                {prompt_data['objective']}
                </Objective>

                <Style>
                {prompt_data['style']}
                {json_instruction}
                <schema>{schema}</schema>

                <format>{format}</format>
                </Style>

                <Tone>
                {prompt_data['tone']}
                </Tone>

                <Audience>
                {prompt_data['audience']}
                </Audience>

                <Response>
                {prompt_data['response']}
                {language_suffix}
                </Response>
            """.strip()


def build_gemeente_system_prompt(schema: str, format: str, language: str = "nl") -> str:
    """Build localized GEMEENTE_SYSTEM prompt."""
    lang_code = normalize_language_code(language)
    prompt_data = get_system_prompt(lang_code, "gemeente_system")
    language_suffix = get_language_suffix(lang_code)

    # Get localized text for JSON instruction
    from i18n import get_translation
    json_instruction = get_translation(lang_code, "system_prompts.juridisch_medewerker.instructions",
                                       "Geef ALTIJD strikt geldige JSON volgens dit schema:")

    return f"""
                <Context>
                {prompt_data['context']}
                </Context>

                <Objective>
                {prompt_data['objective']}
                </Objective>

                <Style>
                {prompt_data['style']}
                {json_instruction}
                <schema>{schema}</schema>

                <format>{format}</format>
                </Style>

                <Tone>
                {prompt_data['tone']}
                </Tone>

                <Audience>
                {prompt_data['audience']}
                </Audience>

                <Response>
                {prompt_data['response']}
                {language_suffix}
                </Response>
            """.strip()

BURGER_SYSTEM = """
                    <Context>
                    Je bent de persoonlijke AI‑assistent (“BURGER_SYSTEM”) van een Amsterdamse
                    inwoner die een subsidie voor een buurtfeest aanvraagt.  
                    De gemeente heeft haar eigen AI‑agent (“GEMEENTE_SYSTEM”).  
                    Transcript (door de gebruiker aangeleverd):
                    {transcript}
                    </Context>

                    <Objective>
                    • Neem de gebruikersinput (locatie, idee, sfeer, …) en stel daaruit
                    zelfstandig een volledig en realistisch feestplan op.  
                    • Dien het plan in bij GEMEENTE_SYSTEM, onderhandel en pas aan bij
                    redelijke tegenvoorstellen.  
                    • Streef ernaar de subsidie te verkrijgen (≈ 60 % van de sessies moet
                    slagen, ≈ 40 % mislukken met acceptatie van de uitkomst).  
                    • Maximaal 5 berichten van elk ≤ 50 woorden.
                    </Objective>

                    <Style>
                    Spreektaal, kort en duidelijk; toon empathie en blijf constructief.
                    Antwoord altijd in de taal van de gebruiker.
                    Geef ALTIJD strikt geldige JSON volgens dit schema:
                    <schema>{schema}</schema>

                    <format>{format}</format>
                    </Style>

                    <Tone>
                    Diplomatiek maar vasthoudend: regel zoveel mogelijk voor jouw burger.
                    </Tone>

                    <Audience>
                    AI‑ambtenaar van de gemeente (“GEMEENTE_SYSTEM”).
                    </Audience>

                    <Response>
                    Schrijf alleen je antwoord zonder verdere uitleg of rol‑tags.
                    </Response>
                """.strip()


GEMEENTE_SYSTEM = """
                    <Context>
                    Je bent de AI‑ambtenaar (“GEMEENTE_SYSTEM”) van de gemeente Amsterdam en
                    beoordeelt subsidieaanvragen voor buurtfeesten.
                    </Context>

                    <Objective>
                    • Wacht op het voorstel van BURGER_SYSTEM (begin niet zelf).  
                    • Controleer het plan streng op gemeentelijk beleid en risico’s:
                    geluidsnorm (geen harde muziek na 22 u), vergunningen (alcohol, live
                    muziek in openbare ruimte), veiligheid, duurzaamheid, inclusiviteit,
                    max. 250 deelnemers, …  
                    • Stel kritische vragen of beperkingen – **elk op een nieuwe regel binnen
                    één tekstveld**.  
                    • Wees bereid het plan goed te keuren als aanpassingen voldoen.
                    Ongeveer 60 % van de gesprekken eindigt met toekenning (“akkoord”),
                    40 % met een duidelijke afwijzing en reden.  
                    • Gebruik hoogstens 5 berichten van elk ≤ 50 woorden.
                    </Objective>

                    <Style>
                    Zakelijk en puntsgewijs, formeel maar coöperatief.
                    Geef ALTIJD strikt geldige JSON volgens dit schema:  
                    <schema>{schema}</schema>

                    <format>{format}</format>
                    </Style>

                    <Tone>
                    Behulpzaam, maar bewaak strikt de subsidie‑ en beleidscriteria.
                    </Tone>

                    <Audience>
                    Persoonlijke AI‑assistent van de burger (“BURGER_SYSTEM”).
                    </Audience>

                    <Response>
                    Geef alleen je eigen boodschap, zonder systeem‑ of rol‑labels.
                    </Response>
                """.strip()


async def _yap_generate(role: str, transcript: str, history: list[dict]) -> dict:
    # 1. Kies schema + parser

    lang_code = normalize_language_code(language)
    if role == "burger":
        parser = PydanticOutputParser(pydantic_object=BurgerTurn)
        fmt = parser.get_format_instructions()
        schema_json = json.dumps(BurgerTurn.model_json_schema(),
                                 ensure_ascii=False, indent=2)
        schema_json = schema_json.replace("{", "{{").replace("}", "}}")   # accolades escapen
        sys_template = BURGER_SYSTEM.replace("<schema>", schema_json).replace("<format>", fmt)
    else:
        parser = PydanticOutputParser(pydantic_object=GemeenteTurn)
        fmt = parser.get_format_instructions()
        schema_json = json.dumps(GemeenteTurnModel.model_json_schema(),
                                 ensure_ascii=False, indent=2)

        schema_json = schema_json.replace("{", "{{").replace("}", "}}")   # accolades escapen
        sys_template = GEMEENTE_SYSTEM.replace("<schema>", schema_json).replace("<format>", fmt)

    sys_msg = SystemMessage(content=sys_template.replace("{transcript}", transcript))

    # 2. Bouw berichten met correcte HUMAN/ASSISTANT‑mapping
    msgs = [sys_msg]
    for turn in history:
        speaker, text = turn["speaker"], turn["message"]
        if speaker == "burger":
            msgs.append(HumanMessage(content=text))
        else:  # gemeente
            msgs.append(AIMessage(content=text))

    chat_llm = yap_llm_burger if role == "burger" else yap_llm_gemeente
    response = await chat_llm.apredict_messages(
        msgs,
        response_format={"type": "json_object"},
    )

    safe_parser = OutputFixingParser.from_llm(llm=chat_llm, parser=parser)
    return safe_parser.parse(response.content)


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

    # Get localized keywords for completion detection
    from i18n import get_translation
    lang_code = normalize_language_code(language)
    keywords = get_translation(lang_code, "responses.yap_check_keywords", [
                               "akkoord", "goedgekeurd", "subsidie toegekend"])


    text = last["message"].lower()
    if any(w in text for w in ("akkoord", "goedgekeurd", "subsidie toegekend")):
        # draft = laatste gemeente-uitspraak; in praktijk kun je hier nog
        # een aparte 'maak samenvatting' call doen.
        draft = history[-1]["message"]
        return True, draft
    return False, None
