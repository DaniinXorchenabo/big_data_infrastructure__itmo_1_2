import pytest
from PIL import Image
import io
from httpx import AsyncClient




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


