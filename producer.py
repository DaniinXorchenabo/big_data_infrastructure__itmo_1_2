import os

from src.configs.config import CONFIG
from src.producer import producer
import uvicorn
# print(os.getcwd())


if __name__ == '__main__':

    uvicorn.run(producer)