from src.core.db.init_db import DB_CONTROLLER


async def get_db():
    with DB_CONTROLLER as db_conn:
        yield db_conn