import fastapi
import uvicorn
from fastapi import FastAPI
from src.web.api.init_api import init_api
from src.web.events.init import ml_lifespan
from src.web.init_app import init_app

app = FastAPI(lifespan=ml_lifespan)


app = init_app(app)



if __name__ == '__main__':
    uvicorn.run(app)