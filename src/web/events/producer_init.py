from contextlib import asynccontextmanager, contextmanager

from fastapi import FastAPI

from src.core.db.init_db import init_db_conn, init_db_conn_sync
from src.core.kafka.init_kafka import init_kafka_conn, init_kafka_conn_sync


@asynccontextmanager
async def producer_lifespan(app: FastAPI):

    # Load the ML model
    async with init_db_conn(app):
        async with init_kafka_conn(app):
            yield

@contextmanager
async def producer_lifespan_sync(app: FastAPI):

    # Load the ML model
    with init_db_conn_sync(app):
        with init_kafka_conn_sync(app):
            yield