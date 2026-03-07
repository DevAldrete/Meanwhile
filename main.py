import asyncio

import uvicorn

from src.api import create_app
from src.config import get_settings
from src.temporal import connect_temporal
from src.worker import create_worker


def main() -> None:
    app = create_app(settings=get_settings())
    uvicorn.run(app, host="0.0.0.0", port=8000)


async def run_worker() -> None:
    settings = get_settings()
    client = await connect_temporal(settings)
    worker = create_worker(client, settings)
    await worker.run()


def worker_main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
