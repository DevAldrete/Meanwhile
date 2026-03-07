from temporalio.worker import Worker
from temporalio.contrib.pydantic import pydantic_data_converter

import pytest

from meanwhile.activities import generate_chat_answer
from meanwhile.models import ChatRequest
from meanwhile.workflows import ChatWorkflow


@pytest.mark.asyncio
async def test_chat_workflow_executes_activity_and_returns_response() -> None:
    from temporalio.testing import WorkflowEnvironment

    env = await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    )
    try:
        async with Worker(
            env.client,
            task_queue="test-chatbot-queue",
            workflows=[ChatWorkflow],
            activities=[generate_chat_answer],
        ):
            request = ChatRequest(
                prompt="What is Temporal?",
                user_id="user-1",
                conversation_id="conv-1",
            )
            result = await env.client.execute_workflow(
                ChatWorkflow.run,
                request,
                id="chat-workflow-test",
                task_queue="test-chatbot-queue",
            )

            assert result.conversation_id == "conv-1"
            assert result.workflow_id == "chat-workflow-test"
            assert result.answer.startswith("Echo:")
    finally:
        await env.shutdown()


@pytest.mark.asyncio
async def test_chat_workflow_signal_and_query() -> None:
    from temporalio.testing import WorkflowEnvironment

    env = await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    )
    try:
        async with Worker(
            env.client,
            task_queue="test-chatbot-signal-queue",
            workflows=[ChatWorkflow],
            activities=[generate_chat_answer],
        ):
            request = ChatRequest(
                prompt="status test",
                user_id="user-2",
                conversation_id="conv-2",
            )
            handle = await env.client.start_workflow(
                ChatWorkflow.run,
                request,
                id="chat-workflow-signal-test",
                task_queue="test-chatbot-signal-queue",
            )

            await handle.signal(ChatWorkflow.set_status, "paused")
            status = await handle.query(ChatWorkflow.get_status)
            assert status in {"paused", "completed"}

            await handle.result()
    finally:
        await env.shutdown()
