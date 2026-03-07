from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from meanwhile.activities import generate_chat_answer
    from meanwhile.models import ChatRequest, ChatResponse


@workflow.defn
class ChatWorkflow:
    def __init__(self) -> None:
        self._status = "created"

    @workflow.run
    async def run(self, request: ChatRequest) -> ChatResponse:
        self._status = "running"
        result = await workflow.execute_activity(
            generate_chat_answer,
            request.prompt,
            start_to_close_timeout=timedelta(seconds=30),
        )
        self._status = "completed"
        return ChatResponse(
            workflow_id=workflow.info().workflow_id,
            run_id=workflow.info().run_id,
            conversation_id=request.conversation_id,
            answer=result.answer,
        )

    @workflow.signal
    async def set_status(self, value: str) -> None:
        self._status = value

    @workflow.query
    def get_status(self) -> str:
        return self._status
