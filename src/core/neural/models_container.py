import dataclasses
from typing import List, Tuple, Type, Any
import gc

import torch
from torchvision.transforms import Compose

from src.configs.config import  CONFIG
from src.core.neural.models.fashion_mnist_lite_model import LightweightFashionMNIST
from src.utils.singleton import singleton

from pytorch_lightning.callbacks import ModelCheckpoint
from torchmetrics.classification import MulticlassF1Score
import uuid
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from torchvision.datasets import FashionMNIST

import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger

import torchmetrics


@dataclasses.dataclass
class ModelVenv:
    model_cl: Type[torch.nn.Module]
    weights_path: str
    transforms: Compose
    model: torch.nn.Module | None = None


@singleton
class ModelsContainer(object):

    def __init__(self):
        self.fashion_mnist_lit_model = ModelVenv(
            model_cl=LightweightFashionMNIST,
            weights_path=CONFIG.fashion_mnist_lit_model_weights,
            transforms=transforms.Compose([
                transforms.Grayscale(),  # убеждаемся, что изображение в оттенках серого
                transforms.Resize((28, 28)),  # изменяем размер до 28x28
                transforms.ToTensor(),
                transforms.Normalize((0.5,), (0.5,))
            ])
        )

        self.model_list = [
            self.fashion_mnist_lit_model,
        ]


    def _load_model(self, venv: ModelVenv):
        model = venv.model_cl()
        state_dict = torch.load(venv.weights_path, map_location=torch.device(CONFIG.DEVICE))
        model.load_state_dict(state_dict)
        model.eval()  # переводим модель в режим инференса
        model.to(CONFIG.DEVICE)
        venv.model = model

    def _clear_model(self, venv: ModelVenv):
        venv.model.cpu()
        del venv.model
        venv.model = None
        gc.collect()  # запускаем сборщик мусора для освобождения памяти
        if torch.cuda.is_available():
            torch.cuda.empty_cache()  # очищаем кеш GPU, если модель была на GPU


    def __enter__(self) -> "ModelsContainer":
        for i in self.model_list:
            self._load_model(i)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for i in self.model_list:
            self._clear_model(i)
        return self


MODELS_CONTAINER = ModelsContainer()
