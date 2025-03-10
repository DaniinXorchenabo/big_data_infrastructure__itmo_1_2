from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.db.init_db import init_db_conn
from src.core.neural.models_container import MODELS_CONTAINER


@asynccontextmanager
async def main_lifespan(app: FastAPI):

    # Load the ML model
    async with (ml_lifespan(app), init_db_conn(app) as db_conn):
        yield


@asynccontextmanager
async def ml_lifespan(app: FastAPI):

    # Load the ML model
    with MODELS_CONTAINER as container:
        yield


def init_events(app: FastAPI):
    return app

