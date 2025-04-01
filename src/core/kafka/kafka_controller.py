import json

from kafka import KafkaProducer, KafkaConsumer

from src.utils.singleton import singleton


@singleton
class KafkaController(object):
    def __init__(self, config):
        self.count = 0
        # Чтение настроек из переменной окружения
        self.KAFKA_BOOTSTRAP_SERVERS =  f'{config.KAFKA_HOST}:{config.KAFKA_PORT}' # os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.config = config
        # Инициализация Kafka Producer
        if config.KAFKA_PRODUCER:
            self.producer = KafkaProducer(
                bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        else:
            self.producer = None

        if config.KAFKA_CONSUMER:
            self.consumer = KafkaConsumer(
                config.KAFKA_TOPIC,
                bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
        else:
            self.consumer = None


    def __enter__(self):
        self.count += 1
        return self

    def __exit__(self, type, value, traceback):
        self.count -= 1
        if self.count == 0:
            ...

    def send(self, message):
        if self.producer:
            self.producer.send(self.config.KAFKA_TOPIC, value=message)
            self.producer.flush()



