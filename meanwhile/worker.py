from temporalio.client import Client
from temporalio.worker import Worker

from meanwhile.activities import (
    create_workflow_run,
    generate_chat_answer,
    load_workflow_definition,
    run_ai_node,
    update_workflow_run_status,
)
from meanwhile.config import AppSettings
from meanwhile.workflows import ChatWorkflow, InterpreterWorkflow


def create_worker(client: Client, settings: AppSettings) -> Worker:
    return Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[ChatWorkflow, InterpreterWorkflow],
        activities=[
            generate_chat_answer,
            load_workflow_definition,
            create_workflow_run,
            update_workflow_run_status,
            run_ai_node,
        ],
    )
