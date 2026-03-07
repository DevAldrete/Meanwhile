from unittest.mock import AsyncMock

import pytest

from meanwhile.activities import generate_chat_answer
from meanwhile.models import ChatResult


@pytest.mark.asyncio
async def test_generate_chat_answer_uses_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_agent = AsyncMock()
    fake_agent.generate.return_value = ChatResult(answer="hello from activity")

    monkeypatch.setattr("meanwhile.activities.get_agent", lambda: fake_agent)

    result = await generate_chat_answer("hello")

    assert result.answer == "hello from activity"
    fake_agent.generate.assert_awaited_once_with("hello")
