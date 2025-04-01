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
from src.core.neural.models_container import MODELS_CONTAINER
from src.web.depends.db_depends import get_db

app = APIRouter(prefix='/neural')


# Endpoint для предсказания
@app.post("/predict")
def predict(
        db_conn: Annotated[DBController, Depends(get_db)],
        request_id: str,
        contents
):
    # Читаем содержимое файла
    # Загружаем изображение через PIL
    # contents = bytes(contents, 'utf-8')
    file_bytes = base64.b64decode(contents)
    image = Image.open(io.BytesIO(file_bytes))
    # Если изображение не в режиме L (grayscale), конвертируем его
    if image.mode != "L":
        image = image.convert("L")
    # Применяем трансформации
    img_tensor = MODELS_CONTAINER.fashion_mnist_lit_model.transforms(image)
    img_tensor = img_tensor.unsqueeze(0)  # добавляем размер батча
    # Выполняем инференс
    with torch.no_grad():
        delta_time = time()
        outputs = MODELS_CONTAINER.fashion_mnist_lit_model.model(img_tensor.to(CONFIG.DEVICE))
        delta_time = time() - delta_time
        predicted_class = torch.argmax(outputs, dim=1).item()
    db_conn.insert_row('user_logs', row_key=str(request_id), data={
        "datetime": f"{datetime.utcnow().strftime('%Y_%m_%d__%H_%M_%S')}",
        "result": str(predicted_class),
        'calc_time': str(delta_time),
    })
    return {"predicted_class": predicted_class, "res_id": request_id}
