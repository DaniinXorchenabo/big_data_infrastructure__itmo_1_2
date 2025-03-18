import _io
import logging
import os
import sys
from io import TextIOWrapper
import io, os

# from src.configs.vault import VaultConfig
from src.utils.singleton import singleton

FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = os.path.join(os.getcwd(), "logfile.log")

f = open("logfile.log", "a")

class FakeFile(TextIOWrapper):
    def __init__(self, *a, fake_buffer=None, **kwargs):
        fake_buffer = fake_buffer or []
        self.output = io.BytesIO()
        super().__init__(self.output, *a,  line_buffering=True, **kwargs)
        self.fake_buffer = fake_buffer

    def write(self, data):
        self.fake_buffer.append(data)

@singleton
class LogController:
    """
        Class for logging behaviour of data exporting - object of ExportingTool class
    """

    def __init__(self, show: bool) -> None:
        """
            Re-defined __init__ method which sets show parametr

        Args:
            show (bool): if set all logs will be shown in terminal
        """
        self.show = show
        self.init_buffer: list[str] = ['']
        self.first_open = False
        self.config: 'VaultConfig' = None
        self.loggers = {

        }
    def __call__(self, config):
        self.config = config
        return self

    def __enter__(self) -> logging.Logger :
        if self.config is None:
            raise ValueError('Please, use `with log_controller_obj(CONFIG) as logger:`')
        self.first_open = True
        logger = self.get_logger('main_logger')
        return logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_console_handler(self) -> logging.StreamHandler:
        """
            Class method the aim of which is getting a console handler to show logs on terminal

        Returns:
            logging.StreamHandler: handler object for streaming output through terminal
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FORMATTER)
        return console_handler

    def get_fake_file_handler(self):
        fake_file_h = logging.StreamHandler(
            stream=FakeFile(fake_buffer=self.init_buffer),
            # fake_buffer=self.init_buffer
        )
        fake_file_h.setFormatter(FORMATTER)
        return fake_file_h

    def get_file_handler(self) -> logging.FileHandler | logging.StreamHandler:
        """
            Class method the aim of which is getting a file handler to write logs in file LOG_FILE

        Returns:
            logging.FileHandler: handler object for streaming output through std::filestream
        """
        if self.config is None:
            return self.get_fake_file_handler()
        file_handler = logging.FileHandler(self.config.LOGS_PATH, mode='w')
        file_handler.setFormatter(FORMATTER)
        return file_handler

    def get_logger(self, logger_name: str) -> logging.Logger:
        """
            Class method which creates logger with certain name

        Args:
            logger_name (str): name for logger

        Returns:
            logger: object of Logger class
        """
        if logger_name in self.loggers:
            return self.loggers[logger_name]

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        if self.first_open:
            logger.addHandler(self.get_file_handler())
        else:
            logger.addHandler(self.get_fake_file_handler())

        if self.first_open and bool(self.init_buffer):
            with open(self.config.LOGS_PATH, 'a') as log_file:
                [log_file.write(i) for i in self.init_buffer]
            self.init_buffer.clear()
        if self.show:
            logger.addHandler(self.get_console_handler())
        self.loggers[logger_name] = logger
        logger.debug(f'{logger_name} initialized')
        return logger


logController = LogController(True)
console_only_logger = logController.get_logger('pre_init_console_logger_' + __name__)

