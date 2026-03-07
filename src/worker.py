from temporalio.client import Client
from temporalio.worker import Worker

from meanwhile.activities import generate_chat_answer
from meanwhile.config import AppSettings
from meanwhile.workflows import ChatWorkflow


def create_worker(client: Client, settings: AppSettings) -> Worker:
    return Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[ChatWorkflow],
        activities=[generate_chat_answer],
    )
