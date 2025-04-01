import uvicorn
from fastapi import FastAPI

from src.web.events.producer_init import producer_lifespan
from src.web.init_app import  init_producer

producer = FastAPI(lifespan=producer_lifespan)


producer = init_producer(producer)



if __name__ == '__main__':
    uvicorn.run(producer)