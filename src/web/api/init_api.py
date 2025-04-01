from fastapi import FastAPI
from starlette.responses import RedirectResponse
from src.web.api.neural.consumer_view import app as neural_app
from src.web.api.neural.producer_view import app as neural_producer_app

from src.web.api.statistic.view import app as statistic_app


def init_base_api(app: FastAPI) -> FastAPI:

    @app.get("/")
    async def redirect():
        return RedirectResponse(url="/docs")

    @app.get("/healthcheck")
    async def healthcheck():
        return 'ok'

    # app.include_router(neural_app)
    # app.include_router(statistic_app)

    return app

def init_producer_api(app: FastAPI) -> FastAPI:
    app.include_router(statistic_app)
    app.include_router(neural_producer_app)
    return app


def init_consumer_api(app: FastAPI) -> FastAPI:
    app.include_router(neural_app)
    return app

