import pytest
from PIL import Image
import io
from httpx import AsyncClient


def create_test_image() -> bytes:
    """Создает тестовое изображение в градациях серого."""
    image = Image.new("L", (28, 28), color=128)  # FashionMNIST использует 28x28
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    return img_bytes.getvalue()

@pytest.mark.asyncio(scope="session")
async def test_healthcheck(my_client: AsyncClient):
    client: AsyncClient = my_client
    response = await client.get("/healthcheck")  # /healthcheck
    assert response.status_code == 200
    assert response.json() == "ok"


@pytest.mark.asyncio(scope="session")
async def test_redirect(my_client: AsyncClient):
    response = await my_client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"

@pytest.mark.asyncio(scope="session")
async def test_predict(my_client: AsyncClient):
    img_data = create_test_image()
    files = {"file": ("test.png", img_data, "image/png")}
    response = await my_client.post("/neural/predict", files=files)
    assert response.status_code == 200
    assert "predicted_class" in response.json()
    assert isinstance(response.json()["predicted_class"], int)
