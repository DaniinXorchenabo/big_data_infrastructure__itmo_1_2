from fastapi import FastAPI

from src.web.api.neural.consumer_view import app as neural_app




def init_consumer_api(app: FastAPI) -> FastAPI:
    app.include_router(neural_app)
    return app

