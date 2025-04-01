from src.core.kafka.init_kafka import KAFKA_CONTROLLER


async def get_kafka():
    with KAFKA_CONTROLLER as kafka_conn:
        yield kafka_conn
