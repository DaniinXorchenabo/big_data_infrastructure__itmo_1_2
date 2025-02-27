from contextlib import asynccontextmanager

from fastapi import FastAPI
import torch

from src.core.neural.models.fashion_mnist_lite_model import LightweightFashionMNIST
from src.core.neural.models_container import MODELS_CONTAINER


@asynccontextmanager
async def ml_lifespan(app: FastAPI):

    # Load the ML model
    with MODELS_CONTAINER as container:
        yield


def init_events(app: FastAPI):

    return app