from langchain_openai import AzureChatOpenAI
from langchain.output_parsers import PydanticOutputParser
import os
from models import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),  # (alias: azure_deployment)
    api_version=os.getenv("OPENAI_API_VERSION"),
    temperature=0.4,
    streaming=True,
)

def make_chain(step_model: type[BaseModel]):
    """
    Bouwt één LangChain-chain die:
      1. Een lijst BaseMessages maakt uit history + nieuwe user-message
      2. Het model aanroept met structured_output = step_model
      3. Het resultaat in een Pydantic-object parseert
    """

    parser = PydanticOutputParser(pydantic_object=step_model)

    system_msg = SystemMessage(
        content=(
            "Je bent een behulpzame jurist van de gemeente. "
            "Stel alleen vragen die nodig zijn om de checklist af te vinken."
        )
    )

    def to_message(d: dict):
        """Dict {'role': ..., 'content': ...} → juiste BaseMessage"""
        match d["role"]:
            case "user":
                return HumanMessage(content=d["content"])
            case "assistant":
                return AIMessage(content=d["content"])
            case _:
                return SystemMessage(content=d["content"])

    chain = (
        # 1️⃣ lambda → list[BaseMessage]
        (lambda x: [system_msg] +
                   [to_message(m) for m in x["history"]] +
                   [HumanMessage(content=x["message"])])
        # 2️⃣ LLM-call met gestructureerde output
        | llm.with_structured_output(step_model)
        # 3️⃣ Parser → echt Pydantic-object
        | parser
    )
    return chain
