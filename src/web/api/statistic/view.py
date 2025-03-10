from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.core.db.db_controller import DBController
from src.web.depends.db_depends import get_db

app = APIRouter(prefix='/statistic')


# Endpoint для предсказания
@app.get("/res_id/{res_id}")
async def get_res_by_id(db_conn: Annotated[DBController, Depends(get_db)], res_id: UUID):
    result = db_conn.get_row('user_logs', str(res_id))
    return result

# Endpoint для предсказания
@app.get("/all")
async def get_all_results(db_conn: Annotated[DBController, Depends(get_db)]):
    result = db_conn.get_all_rows('user_logs')
    return result

