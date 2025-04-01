from contextlib import asynccontextmanager, contextmanager

from fastapi import FastAPI

from src.core.db.init_db import init_db_conn, init_db_conn_sync
from src.core.kafka.init_kafka import init_kafka_conn, init_kafka_conn_sync
from src.core.neural.models_container import MODELS_CONTAINER


@asynccontextmanager
async def main_lifespan(app: FastAPI):

    # Load the ML model
    async with (ml_lifespan(app)):
        async with init_db_conn(app):
            async with init_kafka_conn(app):
                yield

@contextmanager
def main_lifespan_sync(app: FastAPI):

    # Load the ML model
    with (ml_lifespan_sync(app)):
        with init_db_conn_sync(app):
            with init_kafka_conn_sync(app):
                yield


@asynccontextmanager
async def ml_lifespan(app: FastAPI):

    # Load the ML model
    with MODELS_CONTAINER as container:
        yield

@contextmanager
def ml_lifespan_sync(app: FastAPI):

    # Load the ML model
    with MODELS_CONTAINER as container:
        yield

def init_base_events(app: FastAPI):
    return app

