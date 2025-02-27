import os

from src.configs.config import CONFIG
from src.main import app
import uvicorn
print(os.getcwd())
if __name__ == '__main__':

    uvicorn.run(app)