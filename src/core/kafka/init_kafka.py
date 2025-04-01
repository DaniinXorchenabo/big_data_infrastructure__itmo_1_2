from contextlib import asynccontextmanager, contextmanager

from fastapi import FastAPI

from src.configs.config import CONFIG
from src.core.kafka.kafka_controller import KafkaController


KAFKA_CONTROLLER = KafkaController(CONFIG)


@asynccontextmanager
async def init_kafka_conn(app: FastAPI):
    with KAFKA_CONTROLLER as kafka_conn:
        yield kafka_conn


@contextmanager
def init_kafka_conn_sync(app: FastAPI):
    with KAFKA_CONTROLLER as kafka_conn:
        yield kafka_conn