import asyncio
from functools import lru_cache
from uuid import uuid4

import pytest
from PIL import Image
import io
import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
import logging

from httpx import AsyncClient
from sympy.physics.units import years

from src.configs.config import CONFIG
from src.core.db.db_controller import DBController
from src.core.db.init_db import init_db_conn
from src.web.depends.db_depends import get_db
from src.web.events.init import main_lifespan
from src.web.init_app import init_producer
from tests.configs import BASE_URL


def create_test_image(size: tuple, format: str = 'PNG', id: int = -1) -> bytes:
    """Создает тестовое изображение в градациях серого."""
    image = Image.new("L", size, color=128)  # FashionMNIST использует 28x28
    img_bytes = io.BytesIO()
    image.save(img_bytes, format=format)
    return img_bytes.getvalue()


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
    app = init_producer(app)
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

@pytest_asyncio.fixture(scope="session")
async def first_db_conn(app):
    conn = await anext(get_db())
    yield conn

@pytest_asyncio.fixture(scope="session")
async def clean_db(app, first_db_conn: DBController):
    first_db_conn.delete_all_tables()
    yield first_db_conn

@pytest_asyncio.fixture(scope="session")
async def new_db(app, clean_db: DBController):
    async with init_db_conn(app) as conn:
        yield conn


@pytest_asyncio.fixture(scope="session")
async def db_conn(app, new_db: DBController):
    yield new_db

@pytest_asyncio.fixture(scope="session")
async def db_conn_with_data(app, db_conn: DBController):
    tables = ['test_1']
    inserted_data =  {}
    for table in tables:
        inserted_data[table] = []
        for i in range(100):
            data = {'foo': f'bar_{i}', f'foo2_{i}': 'bar2'}
            _u = str(uuid4())
            db_conn.insert_row(table, _u, data)
            inserted_data[table].append(data | {'id': _u})

    yield db_conn, inserted_data

@pytest_asyncio.fixture(scope="session")
async def images(app):
    _count = 0
    images = [create_test_image((i, ii), f, _count)
              for i in [1, 2, 28, 32,64,128,256,512,1024,2048,4096]
              for ii in [1, 2, 28, 32,64,128,256,512,1024,2048,4096]
              for f in ['PNG']
              if (_count := _count + 1)
              ]
    yield images

@pytest_asyncio.fixture(scope="session")
async def neural_predictions(my_client: AsyncClient, images):
    results = []
    for img_data in images:
        files = {"file": ("test.png", img_data, "image/png")}
        response = await my_client.post("/neural/request_predict", files=files)
        results.append(response)
    yield results, images

