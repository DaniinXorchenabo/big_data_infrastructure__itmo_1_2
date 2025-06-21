from fastapi import FastAPI

from src.web.api.neural.producer_view import app as neural_producer_app
from src.web.api.statistic.view import app as statistic_app



def init_producer_api(app: FastAPI) -> FastAPI:
    app.include_router(statistic_app)
    app.include_router(neural_producer_app)
    return app



