from functools import lru_cache

from temporalio import activity

from meanwhile.agent import ChatbotAgent, PydanticAIChatbotAgent
from meanwhile.config import get_settings
from meanwhile.models import ChatResult


@lru_cache(maxsize=1)
def get_agent() -> ChatbotAgent:
    settings = get_settings()
    return PydanticAIChatbotAgent(model_name=settings.pydantic_ai_model)


@activity.defn
async def generate_chat_answer(prompt: str) -> ChatResult:
    agent = get_agent()
    return await agent.generate(prompt)
