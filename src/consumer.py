import uvicorn
from fastapi import FastAPI
from src.web.events.init import main_lifespan
from src.web.init_app import init_producer, init_consumer

consumer = FastAPI(lifespan=main_lifespan)


consumer = init_consumer(consumer)



if __name__ == '__main__':
    uvicorn.run(consumer)