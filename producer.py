import os

from src.configs.config import CONFIG
import uvicorn

from src.producer import producer


if __name__ == '__main__':

    uvicorn.run(producer)