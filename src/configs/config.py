import os
from collections.abc import Callable

from src.configs import vault
from src.configs.vault import VAULT_READER, VaultConfig
from src.utils.logger.logger import logController
from src.utils.singleton import singleton



@singleton
class Config(object):
    def __init__(self, vault: VaultConfig, LOGGER):
        self.LOGGER = LOGGER

        self.variable_source = {
            'vault': vault.get_vault_secrets,
            'environ variables': os.environ,
        }

        # =========================
        self.DOCKER_USE_GPU = self.bool_var(self.load_variable('DOCKER_USE_GPU'))
        if self.DOCKER_USE_GPU:
            import torch
            self.DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.DEVICE = 'cpu'

        self.ROOT_DIR = vault.ROOT_DIR
        self.LOGS_PATH = vault.LOGS_PATH

        self.WEIGHTS_DIR = os.path.join(self.ROOT_DIR, 'neural', 'weights', 'prod')
        self.MODEL_DIR = os.path.join(self.WEIGHTS_DIR, self.load_variable('AI_WEIGHTS_FILENAME'))

        self.fashion_mnist_lit_model_weights = os.path.join(
            self.WEIGHTS_DIR,
            self.load_variable('AI_WEIGHTS_FILENAME'),
        )
        self.BACKEND_PORT = self.load_variable('BACKEND_PORT')
        self.BACKEND_HOST_URL = self.load_variable('BACKEND_HOST_URL')
        self.BACKEND_MICROSERVICE_DEFAULT_PROTOCOL = self.load_variable('BACKEND_MICROSERVICE_DEFAULT_PROTOCOL')
        self.TEST_FROM_NETWORK = self.bool_var(self.load_variable('TEST_FROM_NETWORK', nullable=True))
        self.AI_WEIGHTS_REPO_FILENAME = self.load_variable('AI_WEIGHTS_REPO_FILENAME')
        self.AI_WEIGHTS_REPO = self.load_variable('AI_WEIGHTS_REPO')

        self.DB_LOGIN = self.load_variable('DB_LOGIN')
        self.DB_PASSWORD = self.load_variable('DB_PASSWORD')
        self.DB_HOST = self.load_variable('DB_HOST')
        self.DB_PORT = self.load_variable('DB_PORT')
        self.DB_CONN_URL = f'http://{self.DB_HOST}:{self.DB_PORT}'
        self._DB_PROPERTIES_FILEPATH = os.path.join(self.ROOT_DIR, 'docker', 'hbase', 'conf', 'hbase-rest-users.properties')

        self.KAFKA_HOST = self.load_variable('KAFKA_HOST')
        self.KAFKA_PORT = self.load_variable('KAFKA_PORT')
        self.KAFKA_TOPIC = self.load_variable('KAFKA_TOPIC')
        self.KAFKA_PRODUCER = self.load_variable('KAFKA_PRODUCER')
        self.KAFKA_CONSUMER = self.load_variable('KAFKA_CONSUMER')

        with open(self._DB_PROPERTIES_FILEPATH, 'w') as f:
            print(f'{self.DB_LOGIN}={self.DB_PASSWORD}', file=f)


    @staticmethod
    def bool_var(val):
        if val is None:
            return None
        return str(val).lower().strip() in ['true', '1', 't', 'y', 'yes']

    def load_variable(self, name, nullable=False):
        res = None
        for k, variable_spase in self.variable_source.items():
            if isinstance(variable_spase, Callable):
                res = variable_spase(name)
            elif name in variable_spase:
                res = variable_spase[name]
            if res is not None:
                self.LOGGER.info(f'Переменная {name} была инициализирована из пространства секретов {k}')
                return res
            else:
                self.LOGGER.info(f'Переменная {name} не была найдена в пространстве секретов {k}')
        if nullable:
            return None
        raise ValueError(f'Переменная {name} не была найдена ни в одном пространстве секретов')


LOGGER = None
with VAULT_READER as vault:
    with logController(vault) as logger:
        LOGGER = logger
        CONFIG = Config(vault, LOGGER)
