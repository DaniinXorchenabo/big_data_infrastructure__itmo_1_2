import pytest
from PIL import Image
import io
from httpx import AsyncClient, Response


@pytest.mark.asyncio(scope="session")
async def test_predict(my_client: AsyncClient, neural_predictions: (list[Response], list[bytes])):
    responses, images = neural_predictions
    for response in responses:
        assert response.status_code == 200
        assert all(i in response.json() for i in ['res_id',])
