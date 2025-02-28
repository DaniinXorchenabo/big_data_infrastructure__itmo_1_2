import os
from functools import reduce

import torch

from src.configs.paths_config import ROOT_DIR
from src.utils.singleton import singleton



@singleton
class Config(object):
    def __init__(self):
        self.DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.ROOT_DIR = ROOT_DIR

        self.WEIGHTS_DIR = os.path.join(self.ROOT_DIR, 'neural', 'weights', 'prod')
        self.MODEL_DIR = os.path.join(self.WEIGHTS_DIR, os.environ.get('AI_WEIGHTS_FILENAME'))

        self.fashion_mnist_lit_model_weights = os.path.join(
            self.WEIGHTS_DIR,
            'fashion_MNIST_lite_af5d8943-4cf8-4204-b7a3-f39e5a49e673.pth'
        )
        self.BACKEND_PORT = os.environ['BACKEND_PORT']
        self.BACKEND_HOST_URL = 'dl'
        self.BACKEND_MICROSERVICE_DEFAULT_PROTOCOL = 'http'
        self.TEST_FROM_NETWORK = self.bool_var(os.environ.get('TEST_FROM_NETWORK', None))

    @staticmethod
    def bool_var(val):
        if val is None:
            return None
        return str(val).lower() in ['true', '1', 't', 'y', 'yes']

CONFIG = Config()
