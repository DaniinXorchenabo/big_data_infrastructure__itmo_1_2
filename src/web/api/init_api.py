from fastapi import FastAPI
from starlette.responses import RedirectResponse
from src.web.api.neural.view import app as neural_app
from src.web.api.statistic.view import app as statistic_app


def init_api(app: FastAPI) -> FastAPI:

    @app.get("/")
    async def redirect():
        return RedirectResponse(url="/docs")

    @app.get("/healthcheck")
    async def healthcheck():
        return 'ok'

    app.include_router(neural_app)
    app.include_router(statistic_app)

    return app