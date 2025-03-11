from uuid import uuid4

import pytest
from PIL import Image
import io
from httpx import AsyncClient

from src.core.db.db_controller import DBController

tables = ['table1', 'table2', 'user_logs', ]


@pytest.mark.asyncio(scope="session")
async def test_db_auth_test(first_db_conn: DBController):
    assert (first_db_conn.auth_headers.get('Authorization')
            and first_db_conn.auth_headers.get('Authorization').startswith('Basic '))


@pytest.mark.asyncio(scope="session")
async def test_db_is_clean_test(clean_db: DBController):
    assert clean_db.get_all_tables() == []


@pytest.mark.asyncio(scope="session")
async def test_double_remove_test(clean_db: DBController):
    clean_db.delete_all_tables()
    assert clean_db.get_all_tables() == []


@pytest.mark.asyncio(scope="session")
async def test_create_tables_with_init_test(new_db: DBController):
    assert set(new_db.get_all_tables()) == set(tables)


@pytest.mark.asyncio(scope="session")
async def test_insert_row_test(db_conn: DBController):
    for table in tables:
        data = {'foo': 'bar'}
        _u = str(uuid4())
        insert_res = db_conn.insert_row(table, _u, data)
        assert insert_res == _u
        res = db_conn.get_row(table, _u)
        assert res == data | {"id": _u}


@pytest.mark.asyncio(scope="session")
async def test_get_test(db_conn_with_data: (DBController, dict)):
    db_conn, inserted_data = db_conn_with_data
    for table, target_res in inserted_data:
        for sample in target_res:
            res = db_conn.get_row(table, sample['id'])
            assert res == sample, f'table: {table}, |{res} != {sample}'

    assert db_conn_with_data.get_row(table, str(uuid4())) is None


@pytest.mark.asyncio(scope="session")
async def test_get_all_rows_test(db_conn_with_data: (DBController, dict)):
    db_conn, inserted_data = db_conn_with_data
    for table, target_res in inserted_data:
        res = db_conn.get_all_rows(table)
        keys_res = {i['id']: i for i in res}
        target_res_keys = {i['id']: i for i in target_res}
        assert (set(keys_res) == set(target_res_keys)
                and len(keys_res) == len(target_res_keys) == len(res) == len(target_res))
        assert all(keys_res[key] == target_res_keys[key] for key in target_res_keys)


@pytest.mark.asyncio(scope="session")
async def test_get_all_rows_from_empty_table_test(db_conn: DBController):
    db_conn, inserted_data = db_conn
    res = db_conn.get_all_rows('test_1')
    assert res == []


@pytest.mark.asyncio(scope="session")
async def test_update_row_test(db_conn_with_data: (DBController, dict)):
    db_conn, inserted_data = db_conn_with_data
    for table, target_res in inserted_data:
        for ind, sample in enumerate(target_res):
            upd_key = db_conn.update_row(table, sample['id'], sample)
            assert upd_key == sample['id']
            res = db_conn.get_row(table, sample['id'])
            assert res == sample, f'table: {table}, |{res} != {sample}'

            upd_key = db_conn.update_row(table, sample['id'], sample | {'foo foo': 'bar'})
            assert upd_key == sample['id']
            res = db_conn.get_row(table, sample['id'])
            assert res == sample | {'foo foo': 'bar'}, f'table: {table}, |{res} != modified_sample'

            upd_key = db_conn.update_row(table, sample['id'], sample | {'foo': 'bar'})
            assert upd_key == sample['id']
            res = db_conn.get_row(table, sample['id'])
            assert res == sample | {'foo': 'bar'}, f'table: {table}, |{res} != modified_sample'

            sample.pop('foo')
            upd_key = db_conn.update_row(table, sample['id'], sample)
            assert upd_key == sample['id']
            res = db_conn.get_row(table, sample['id'])
            assert res == sample, f'table: {table}, |{res} != modified_sample'
            if ind > 10:
                break


@pytest.mark.asyncio(scope="session")
async def test_delete_row_test(db_conn_with_data: (DBController, dict)):
    db_conn, inserted_data = db_conn_with_data
    for table, target_res in inserted_data:
        for sample in target_res:
            del_key = db_conn.delete_row(table, sample['id'])
            assert del_key == sample['id']
            res = db_conn.get_row(table, sample['id'])
            assert res is None

    assert db_conn_with_data.get_row(table, str(uuid4())) is None
