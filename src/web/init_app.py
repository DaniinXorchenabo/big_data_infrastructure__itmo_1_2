from fastapi import FastAPI

from src.web.api.init_api import init_api
from src.web.events.init import init_events


def init_app(app: FastAPI):

    app = init_api(app)
    app = init_events(app)

    return app