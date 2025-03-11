import base64
from time import sleep

import requests

from src.configs.config import CONFIG
from src.utils.singleton import singleton


@singleton
class DBController(object):
    def __init__(self, db_url, login, password):
        self.db_url = db_url
        self._login = login
        self._password = password
        self.auth_headers = {}
        self.conn_counter = 0

    def __enter__(self):
        self.conn_counter += 1
        auth_str = f"{self._login}:{self._password}"
        auth_encoded = base64.b64encode(auth_str.encode()).decode()
        self.auth_headers = {
            "Authorization": f"Basic {auth_encoded}",
            # "Content-Type": "text/xml",
            # "Accept": "text/xml"
        }
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn_counter -= 1
        if self.conn_counter <= 0:
            self.auth_headers = {}

    @staticmethod
    def encode_str(s):
        """Кодирует строку в Base64."""
        return base64.b64encode(s.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decode_base64(value):
        """Функция для декодирования Base64"""
        return base64.b64decode(value).decode("utf-8")

    def check_table_exists(self, table):
        url = f"{self.db_url}/{table}/schema"
        headers = {}
        response = requests.get(url, headers=self.auth_headers | headers)
        if response.status_code == 200:
            # print(f"Таблица '{table}' существует.")
            return True
        elif response.status_code == 404:
            # print(f"Таблица '{table}' не найдена.")
            return False
        else:
            raise IOError(f"Ошибка при проверке таблицы '{table}': {response.status_code}")
            return False

    def create_table(self, table):
        url = f"{self.db_url}/{table}/schema"
        schema_xml = f"""<?xml version="1.0"?>
    <TableSchema name="{table}">
      <ColumnSchema name="cf"/>
    </TableSchema>"""
        headers = {"Content-Type": "text/xml", "Accept": "application/json",}
        response = requests.post(url, data=schema_xml, headers=self.auth_headers | headers)
        if response.status_code in (200, 201):
            return table
        else:
            raise IOError(f"Не удалось создать таблицу '{table}': {response.status_code}, {response.text}")

    def insert_row(self, table, row_key, data):
        """
        Вставляет строку в таблицу.
        data – словарь вида { "column": "value", ... }.
        В этом примере колонка формируется как 'cf:column'.
        """
        row_encoded = self.encode_str(row_key)
        cells = ""
        for col, val in data.items():
            col_full = f"cf:{col}"
            cells += f'<Cell column="{self.encode_str(col_full)}">{self.encode_str(val)}</Cell>'
        cellset_xml = f"""<?xml version="1.0"?>
    <CellSet>
      <Row key="{row_encoded}">
        {cells}
      </Row>
    </CellSet>"""
        url = f"{self.db_url}/{table}/{row_key}"
        headers = {"Content-Type": "text/xml", "Accept": "application/json",}
        response = requests.put(url, data=cellset_xml, headers=self.auth_headers | headers)
        if response.status_code in (200, 201):
            # print(f"Строка '{row_key}' вставлена в таблицу '{table}'.")
            return row_key
        else:
            raise IOError(
                f"Ошибка вставки строки '{row_key}' в таблицу '{table}': {response.status_code}, {response.text}")
            # print(f"Ошибка вставки строки '{row_key}' в таблицу '{table}': {response.status_code}, {response.text}")

    def get_row(self, table, row_key):
        url = f"{self.db_url}/{table}/{row_key}"
        headers = { "Accept": "application/json",}
        response = requests.get(url, headers=self.auth_headers | headers)
        if response.status_code == 200:
            # print(f"Строка '{row_key}' получена:")
            # print(response.text)
            data = response.json()  # Возвращает данные в формате JSON
            records = self.db_ans_decode(data)
            if bool(records):
                return records[0]
            else:
                return None
        else:
            # print(f"Ошибка получения строки '{row_key}' из таблицы '{table}': {response.status_code}, {response.text}")
            return None

    def update_row(self, table, row_key, data):
        # Обновление строки производится путем повторного вызова insert_row,
        # так как HBase REST перезаписывает данные для указанного row_key.
        # print(f"Обновление строки '{row_key}' в таблице '{table}'...")
        return self.insert_row(table, row_key, data)

    def delete_row(self, table, row_key):
        url = f"{self.db_url}/{table}/{row_key}"
        headers = {}
        response = requests.delete(url, headers=self.auth_headers | headers)
        if response.status_code == 200:
            return row_key
            # print(f"Строка '{row_key}' удалена из таблицы '{table}'.")
        else:
            # print(f"Ошибка удаления строки '{row_key}' из таблицы '{table}': {response.status_code}, {response.text}")
            return None

    def get_all_rows(self, table):
        """Получает все записи из таблицы HBase через REST API с Kerberos-аутентификацией."""
        # headers = {"Accept": "application/json"}
        url = f"{self.db_url}/{table}/scanner"
        # headers = {"Accept": "application/json"} # Укажи правильный хост

        # Устанавливаем Kerberos-аутентификацию
        # auth = HTTPKerberosAuth()
        headers = {
            "Accept": "application/json",
            "Content-Type": "text/xml"
        }
        scanner_xml = """<Scanner batch="100" />"""  # Можно указать количество записей на запрос

        # response = requests.post(url, headers=headers, )
        try:
            # Создаем scanner
            response = requests.post(url, headers=self.auth_headers | headers, data=scanner_xml)
            if response.status_code not in [200, 201]:
                # print(f"Ошибка при создании сканера: {response.text}")
                raise IOError(f"Ошибка при создании сканера: {response.text}")
                return None

            print(response.text, response.status_code, response.headers, response.headers.get("Location"))
            # return response.json()
            # Получаем scanner ID
            scanner_url = response.headers.get("Location")
            if not scanner_url:
                # print("Не удалось получить scanner ID")
                raise IOError("Не удалось получить scanner ID")
                return None

            # Сканируем таблицу
            response = requests.get(scanner_url, headers=self.auth_headers | headers | {"Accept": "application/json"})
            if response.status_code == 204:
                # print("Таблица существует, но данных в ней нет.")
                return []
            if response.status_code != 200:
                # print(f"Ошибка при получении данных: {response.text}")
                raise IOError(f"Ошибка при получении данных: {response.text}")
                return None

            data = response.json()  # Возвращает данные в формате JSON
            records = self.db_ans_decode(data)

            return records

        except Exception as e:
            raise Exception(f'ошибка: {e}') from e
            return None

    def get_all_tables(self):
        """Получает список всех таблиц в HBase."""
        url = f"{self.db_url}/"
        headers = {"Accept": "application/json",}
        response = requests.get(url, headers=self.auth_headers | headers)

        if response.status_code == 200:
            print(response.text)
            return response.json().get("table", [])
        else:
            raise IOError(f"Ошибка при получении списка таблиц: {response.text}")
            return []

    def is_table_enabled(self, table_name):
        """Проверяет, включена ли таблица."""
        url = f"{self.db_url}/{table_name}/schema"
        response = requests.get(url, headers=self.auth_headers | {
                "Content-Type": "application/json",
                "Accept": "application/json",
            })
        if response.status_code == 200:
            return response.json().get("Table", {}).get("enabled", "true") == "true"
        return False  # Если ошибка — считаем, что таблица отключена.

    def delete_table(self, table_name):
        """Отключает и удаляет таблицу в HBase."""
        disable_url = f"{self.db_url}/{table_name}/schema"
        delete_url = f"{self.db_url}/{table_name}"

        """Отключает таблицу (если она включена)."""
        if not self.is_table_enabled(table_name):
            print(f"Таблица {table_name} уже отключена.")
            # return True
        else:
            # Отключаем таблицу
            disable_data = """{"Table":{"@name":"%s", "enabled":"false"}}""" % table_name
            # disable_data = '{"Table": {{"@name": "{table_name}", "enabled": "false"}}}}'

            # response = requests.put(
            #     disable_url,
            #     data=disable_data,
            #     headers=self.auth_headers | {
            #         "Content-Type": "application/json",
            #         # "Accept": "application/json",
            #     },
            # )
            # sleep(0.5)
            # print('------====----------', response.status_code)
            # if response.status_code not in [200, 201]:
            #     raise IOError(f"Ошибка при отключении таблицы {table_name}: {response.text}")
            #     return False

        # Удаляем таблицу
        response = requests.delete(delete_url, headers=self.auth_headers)
        sleep(0.5)
        if response.status_code == 200 or response.status_code == 404:
            # print(f"Таблица {table_name} успешно удалена.")
            return True
        else:
            raise IOError(f"Ошибка при удалении таблицы {table_name}: {response.text}")
            return False

    def delete_all_tables(self):
        """Удаляет все таблицы в HBase."""
        tables = self.get_all_tables()

        if not tables:
            # print("В HBase нет таблиц для удаления.")
            return

        for table in tables:
            self.delete_table(table['name'])

    def db_ans_decode(self, data):
        # 3. Декодируем row key и содержимое
        records = []
        for row in data.get("Row", []):
            row_key = self.decode_base64(row["key"])  # Декодируем ключ строки
            record = {"id": row_key}

            for cell in row.get("Cell", []):
                column_name = self.decode_base64(cell["column"])  # Декодируем имя столбца
                value = self.decode_base64(cell["$"])  # Декодируем значение
                record[column_name.removeprefix('cf:')] = value

            records.append(record)
        return records