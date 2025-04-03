from fastapi import FastAPI

from src.web.api.init_commun_api import init_base_api
from src.web.api.init_consumer_api import init_consumer_api
from src.web.events.common_init import init_base_events


def init_consumer(app: FastAPI):
    app = init_base_api(app)
    app = init_consumer_api(app)
    app = init_base_events(app)

    return app

