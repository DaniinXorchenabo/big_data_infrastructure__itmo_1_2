import json
import traceback

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.admin.new_partitions import NewPartitions
from kafka.errors import TopicAlreadyExistsError

from src.configs.config import LOGGER
from src.utils.singleton import singleton


@singleton
class KafkaController(object):
    def __init__(self, config):
        self.count = 0
        # Чтение настроек из переменной окружения
        self.KAFKA_BOOTSTRAP_SERVERS =  f'{config.KAFKA_HOST}:{config.KAFKA_PORT}' # os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.config = config
        # Инициализация Kafka Producer

        admin_client = KafkaAdminClient(bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS)
        kafka_topics = admin_client._client.cluster.topics()
        if bool(kafka_topics) is False:
            try:
                kafka_topics.add(NewTopic(
                    name=self.config.KAFKA_TOPIC,
                    num_partitions=config.KAFKA_PARTITION_COUNT,
                    replication_factor=1))
                admin_client.create_topics(new_topics=kafka_topics, validate_only=False)
            except TopicAlreadyExistsError as e:
                LOGGER.warn(e)
                LOGGER.debug(traceback.format_exc())
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



