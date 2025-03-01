import io
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import torch
from fastapi.routing import APIRouter

from src.configs.config import CONFIG
from src.core.neural.models_container import MODELS_CONTAINER


app = APIRouter(prefix='/neural')


# Endpoint для предсказания
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Читаем содержимое файла
    contents = await file.read()
    # Загружаем изображение через PIL
    image = Image.open(io.BytesIO(contents))
    # Если изображение не в режиме L (grayscale), конвертируем его
    if image.mode != "L":
        image = image.convert("L")
    # Применяем трансформации
    img_tensor = MODELS_CONTAINER.fashion_mnist_lit_model.transforms(image)
    img_tensor = img_tensor.unsqueeze(0)  # добавляем размер батча
    # Выполняем инференс
    with torch.no_grad():
        outputs = MODELS_CONTAINER.fashion_mnist_lit_model.model(img_tensor.to(CONFIG.DEVICE))
        predicted_class = torch.argmax(outputs, dim=1).item()
    return {"predicted_class": predicted_class}