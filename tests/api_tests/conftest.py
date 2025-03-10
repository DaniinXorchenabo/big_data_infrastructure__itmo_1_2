import asyncio
from functools import lru_cache

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
import logging

from src.configs.config import CONFIG
from src.web.events.init import main_lifespan
from src.web.init_app import init_app
from tests.configs import BASE_URL


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()



@lru_cache(maxsize=None)
def create_app():

    app = FastAPI(lifespan=main_lifespan)
    app = init_app(app)
    return app


@pytest_asyncio.fixture(scope="session")
async def app():
    app = create_app()
    async with LifespanManager(app) as manager:
        yield manager.app


@pytest_asyncio.fixture(scope="session")
async def my_client(app):
    logging.basicConfig()
    async with httpx.AsyncClient(
            base_url=BASE_URL,
            **({} if CONFIG.TEST_FROM_NETWORK else dict(transport=httpx.ASGITransport(app=app)))
    ) as client:
        yield client

