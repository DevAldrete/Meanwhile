from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from meanwhile.config import AppSettings


async def connect_temporal(settings: AppSettings) -> Client:
    return await Client.connect(
        settings.temporal_target,
        namespace=settings.temporal_namespace,
        data_converter=pydantic_data_converter,
    )
