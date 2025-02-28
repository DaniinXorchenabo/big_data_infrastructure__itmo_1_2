import dataclasses
from typing import List, Tuple, Type, Any
import gc
import os
import shutil

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
from huggingface_hub import hf_hub_download
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
import torchmetrics

from src.configs.config import CONFIG


@dataclasses.dataclass
class ModelVenv:
    model_cl: Type[torch.nn.Module]
    weights_path: str
    weights_repo: str
    weights_repo_path: str
    transforms: Compose
    model: torch.nn.Module | None = None,



@singleton
class ModelsContainer(object):

    def __init__(self):
        self.fashion_mnist_lit_model = ModelVenv(
            model_cl=LightweightFashionMNIST,
            weights_path=CONFIG.fashion_mnist_lit_model_weights,
            weights_repo=CONFIG.AI_WEIGHTS_REPO,
            weights_repo_path=CONFIG.AI_WEIGHTS_REPO_FILENAME,
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
        for i in self.model_list:
            self.model_load(i)

    @staticmethod
    def model_load(venv: ModelVenv):
        if os.path.isfile(CONFIG.MODEL_DIR):
            model_path = hf_hub_download(repo_id=venv.weights_repo, filename=venv.weights_repo_path)
            source_dir = model_path
            target_dir = venv.weights_path
            shutil.move(source_dir, target_dir)

    @staticmethod
    def _load_model( venv: ModelVenv):
        model = venv.model_cl()
        state_dict = torch.load(venv.weights_path, map_location=torch.device(CONFIG.DEVICE))
        model.load_state_dict(state_dict)
        model.eval()  # переводим модель в режим инференса
        model.to(CONFIG.DEVICE)
        venv.model = model

    @staticmethod
    def _clear_model( venv: ModelVenv):
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
