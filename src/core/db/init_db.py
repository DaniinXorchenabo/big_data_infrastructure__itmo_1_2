import base64
from contextlib import asynccontextmanager, contextmanager

import requests
from fastapi import FastAPI

from src.configs.config import CONFIG
from src.core.db.db_controller import DBController


DB_CONTROLLER = DBController(CONFIG.DB_CONN_URL, CONFIG.DB_LOGIN, CONFIG.DB_PASSWORD)

@asynccontextmanager
async def init_db_conn(app: FastAPI):
    tables_list = [
        'table1',
        'table2',
        'user_logs',
        'neural_request',
    ]
    with DB_CONTROLLER as conn:
        for table in tables_list:
            if conn.check_table_exists(table) is False:
                conn.create_table(table)
        yield conn

@contextmanager
def init_db_conn_sync(app: FastAPI):
    tables_list = [
        'table1',
        'table2',
        'user_logs',
        'neural_request',
    ]
    with DB_CONTROLLER as conn:
        for table in tables_list:
            if conn.check_table_exists(table) is False:
                conn.create_table(table)
        yield conn