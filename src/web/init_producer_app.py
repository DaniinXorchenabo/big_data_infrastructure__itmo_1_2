from fastapi import FastAPI

from src.web.api.init_commun_api import init_base_api
from src.web.api.init_producer_api import init_producer_api
from src.web.events.common_init import init_base_events


def init_producer(app: FastAPI):
    app = init_base_api(app)
    app = init_producer_api(app)
    app = init_base_events(app)

    return app


