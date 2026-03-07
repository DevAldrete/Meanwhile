from temporalio.worker import Replayer, Worker
from temporalio.contrib.pydantic import pydantic_data_converter

import pytest

from meanwhile.activities import generate_chat_answer
from meanwhile.models import ChatRequest
from meanwhile.workflows import ChatWorkflow


@pytest.mark.asyncio
@pytest.mark.replay
async def test_chat_workflow_replay_determinism() -> None:
    from temporalio.testing import WorkflowEnvironment

    env = await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    )
    try:
        async with Worker(
            env.client,
            task_queue="test-chatbot-replay-queue",
            workflows=[ChatWorkflow],
            activities=[generate_chat_answer],
        ):
            request = ChatRequest(
                prompt="determinism check",
                user_id="user-3",
                conversation_id="conv-3",
            )
            handle = await env.client.start_workflow(
                ChatWorkflow.run,
                request,
                id="chat-workflow-replay-test",
                task_queue="test-chatbot-replay-queue",
            )
            await handle.result()
            history = await handle.fetch_history()

        replayer = Replayer(workflows=[ChatWorkflow])
        await replayer.replay_workflow(history)
    finally:
        await env.shutdown()
