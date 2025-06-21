import uvicorn
from fastapi import FastAPI
from src.web.events.consumer_init import consumer_lifespan
from src.web.init_consumer_app import  init_consumer

consumer = FastAPI(lifespan=consumer_lifespan)


consumer = init_consumer(consumer)



if __name__ == '__main__':
    uvicorn.run(consumer)