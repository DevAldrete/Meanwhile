from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from meanwhile.models import ChatResult


class ChatbotAgent:
    async def generate(self, prompt: str) -> ChatResult:
        raise NotImplementedError


class PydanticAIChatbotAgent(ChatbotAgent):
    def __init__(self, model_name: str = "test"):
        if model_name == "test":
            self._agent = Agent(
                TestModel(
                    custom_output_args={
                        "answer": "Echo: deterministic Temporal test reply"
                    }
                ),
                output_type=ChatResult,
                instructions="You are a concise chatbot used to test Temporal workflow orchestration.",
            )
        else:
            self._agent = Agent(
                output_type=ChatResult,
                instructions="You are a concise chatbot used to test Temporal workflow orchestration.",
            )

    async def generate(self, prompt: str) -> ChatResult:
        result = await self._agent.run(prompt)
        return result.output
