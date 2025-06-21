import os
import time
import traceback

from src.configs.config import CONFIG, LOGGER
from src.consumer import consumer
import uvicorn

from src.core.db.init_db import init_db_conn_sync
from src.core.kafka.init_kafka import KAFKA_CONTROLLER
from src.web.api.neural.consumer_view import predict
from src.web.events.consumer_init import consumer_lifespan_sync

# print(os.getcwd())


if __name__ == '__main__':
    # uvicorn.run(consumer)
    while True:
        try:
            with consumer_lifespan_sync(None):
                with KAFKA_CONTROLLER as kafka_conn:
                    with init_db_conn_sync(None) as db_conn:
                    # print(f"Consumer запущен и прослушивает топик '{topic}'")
                        while True:
                            for msg in kafka_conn.consumer:
                                try:
                                    # LOGGER.info(msg)
                                    predict(db_conn, msg.value['request_kafka_id'],  msg.value['contents'])
                                except Exception as e:
                                    LOGGER.error(e)
                                    LOGGER.error(traceback.format_exc())
        except Exception as e:
            LOGGER.critical(e)
            LOGGER.critical(traceback.format_exc())
            time.sleep(1)