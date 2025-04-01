import base64
import io
from datetime import datetime
from time import time
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile, Depends
from PIL import Image
import torch
from fastapi.routing import APIRouter

from src.configs.config import CONFIG
from src.core.db.db_controller import DBController
from src.core.kafka.kafka_controller import KafkaController
from src.core.neural.models_container import MODELS_CONTAINER
from src.web.depends.db_depends import get_db
from src.web.depends.kafka_depends import get_kafka

app = APIRouter(prefix='/neural')


# Endpoint для предсказания
@app.post("/request_predict")
async def request_predict(
        db_conn: Annotated[DBController, Depends(get_db)],
        kafka_conn: Annotated[KafkaController, Depends(get_kafka)],
        file: UploadFile = File(...),

):
    # Читаем содержимое файла
    contents = await file.read()
    encoded_data = base64.b64encode(contents).decode('utf-8')
    # Загружаем изображение через PIL
    request_kafka_id = str(uuid4())
    kafka_conn.send({
        "request_kafka_id": request_kafka_id,
        "contents": encoded_data,
    })

    db_conn.insert_row('user_logs', row_key=str(request_kafka_id), data={
        "datetime": f"{datetime.utcnow().strftime('%Y_%m_%d__%H_%M_%S')}",
        "request_id": str(request_kafka_id),
    })
    return {"res_id": request_kafka_id}
