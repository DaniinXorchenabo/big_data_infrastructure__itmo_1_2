# test_app.py
import asyncio
from contextlib import asynccontextmanager
from functools import lru_cache
from os.path import join, split

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from orjson import orjson
from pytest_asyncio import is_async_test
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
import logging

from src.configs.config import CONFIG
from src.web.events.init import ml_lifespan
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

    app = FastAPI(lifespan=ml_lifespan)
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

