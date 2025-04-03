import os
import traceback
from datetime import datetime

import hvac

from src.utils.logger.logger import logController
from src.utils.singleton import singleton
from src.configs.paths_config import ROOT_DIR

@singleton
class VaultConfig(object):
    def __init__(self):
        self.VAULT_UNSEAL_KEYS = [os.environ.get(f'VAULT_UNSEAL_KEY_{i}') for i in range(10)]
        self.VAULT_ROOT_TOKEN = os.environ.get(f'VAULT_ROOT_TOKEN')
        self.VAULT_HOST = os.environ[f'VAULT_HOST']
        self.VAULT_PORT = 8200
        self.VAULT_PROTOCOL = 'http'
        self.VAULT_ADDR = f'{self.VAULT_PROTOCOL}://{self.VAULT_HOST}:{self.VAULT_PORT}'
        self.VAULT_SECRETS_PATH = os.environ[f'VAULT_SECRETS_PATH']
        self.VAULT_SECRETS_NAME = os.environ[f'VAULT_SECRETS_NAME']
        self._vault_client = None
        self._auth_vault_client = None

        self.ROOT_DIR = ROOT_DIR
        self.LOGS_PATH = os.path.join(self.ROOT_DIR, 'neural', 'logs', 'prod', f"{(u_:=datetime.utcnow().strftime('%Y_%m_%d__%H_%M_%S'))}.log")

        self.logger = None


    def __enter__(self):
        with logController(self) as logger:
            self.logger = logger
            # Инициализация клиента Vault
            self._vault_client = hvac.Client(url=self.VAULT_ADDR)

            # Проверка состояния хранилища перед разблокировкой
            if self._vault_client.sys.is_sealed():
                logger.info("Хранилище запечатано. Начинаем процесс разблокировки...")
                self.unseal_vault()
                if not self._vault_client.sys.is_sealed():
                    logger.info("Хранилище успешно разблокировано.")
                else:
                    logger.info("Не удалось полностью разблокировать хранилище. Возможно, требуется больше ключей.")
            else:
                logger.info("Хранилище уже разблокировано.")

            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_vault_secrets(self, secret_name):
        with logController(self) as logger:
            self.logger = logger
            if not self.VAULT_ROOT_TOKEN:
                raise EnvironmentError("Переменная окружения VAULT_ROOT_TOKEN не установлена")

            # Инициализируем клиент Vault (предполагается, что Vault доступен по http://127.0.0.1:8200)
            self._auth_vault_client = hvac.Client(url=self.VAULT_ADDR, token=self.VAULT_ROOT_TOKEN)

            # Проверяем, что аутентификация прошла успешно
            if not self._auth_vault_client.is_authenticated():
                raise Exception("Аутентификация в Vault не удалась")

            # Предположим, что секрет сохранён в kv engine версии 2 по пути secret/my-secret.
            # В этом примере используется mount_point 'secret' и путь 'my-secret'
            try:
                logger.info([self.VAULT_SECRETS_NAME])
                logger.info([self.VAULT_SECRETS_PATH])
                logger.info([secret_name])
                secret_response = self._auth_vault_client.secrets.kv.v2.read_secret_version(
                    path=f"{self.VAULT_SECRETS_NAME}/{secret_name}",
                    mount_point=f"{self.VAULT_SECRETS_PATH}"
                )
                logger.info(secret_response)
                secret_data = secret_response['data']['key'].strip()
                # logger.info("Полученные секреты:")
                return secret_data
            except hvac.exceptions.InvalidPath as e:
                return None
            except Exception as e:
                logger.critical("Ошибка при получении секрета:", e)
                raise e from e


    # Функция для разблокировки хранилища
    def unseal_vault(self):
        for ind, key in enumerate(self.VAULT_UNSEAL_KEYS, 1):
            if key is None or key == '':
                self.logger.info(f"unseal-ключ # {ind} пустой.")
                continue
            if self._vault_client.sys.is_sealed():
                try:
                    self._vault_client.sys.submit_unseal_key(key)
                    self.logger.info(f"Применён unseal-ключ # {ind}.")
                except hvac.exceptions.InvalidRequest as e:
                    self.logger.warn(f"Применение unseal-ключа # {ind} прошло неудачно.")
                    self.logger.warn(e)
                    self.logger.debug(traceback.format_exc())
                    continue
            else:
                self.logger.info("Хранилище уже разблокировано.")
                break


VAULT_READER = VaultConfig()
