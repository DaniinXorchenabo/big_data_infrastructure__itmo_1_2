from fastapi import FastAPI

from src.web.api.init_api import init_base_api, init_producer_api, init_consumer_api
from src.web.events.common_init import init_base_events


def init_app_as_once(app: FastAPI):

    app = init_base_api(app)
    app = init_base_events(app)

    return app

def init_producer(app: FastAPI):
    app = init_base_api(app)
    app = init_producer_api(app)
    app = init_base_events(app)

    return app

def init_consumer(app: FastAPI):
    app = init_base_api(app)
    app = init_consumer_api(app)
    app = init_base_events(app)

    return app

