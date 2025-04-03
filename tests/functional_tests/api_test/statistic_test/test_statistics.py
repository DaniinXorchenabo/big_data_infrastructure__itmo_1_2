from uuid import uuid4

import pytest
from PIL import Image
import io
from httpx import AsyncClient, Response

from src.core.db.db_controller import DBController


@pytest.mark.asyncio(scope="session")
async def test_get_all_res(my_client: AsyncClient, db_conn: DBController):
    client: AsyncClient = my_client
    response = await client.get("/statistic/all")  # /healthcheck
    assert response.status_code == 200
    # assert response.text == 'null'

@pytest.mark.asyncio(scope="session")
async def test_get_all_results(my_client: AsyncClient, neural_predictions: (list[Response], list[bytes])):
    data = {response.json()['res_id']: response.json() for response in neural_predictions[0]}
    response = await my_client.get(f"/statistic/all")
    assert response.status_code == 200
    response_data = {i['id']: i for i in response.json()}


@pytest.mark.asyncio(scope="session")
async def test_get_res_by_id_with_empty_table(my_client: AsyncClient, db_conn: DBController):
    response = await my_client.get(f"/statistic/res_id/{str(uuid4())}")
    assert response.status_code == 200
    assert response.text == 'null'


@pytest.mark.asyncio(scope="session")
async def test_get_res_by_id(my_client: AsyncClient, neural_predictions: (list[Response], list[bytes])):
    data = [response.json() for response in neural_predictions[0]]
    for res_data in data:
        response = await my_client.get(f"/statistic/res_id/{res_data['res_id']}")
        assert response.status_code == 200
        assert set(response.json()) == {'id', "datetime", "result", 'calc_time',}
        assert response.json()['id'] == res_data['res_id']
        # assert str(response.json()['result']) == str(res_data['predicted_class'])
