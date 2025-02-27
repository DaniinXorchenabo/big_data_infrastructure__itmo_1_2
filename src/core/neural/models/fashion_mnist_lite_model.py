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


class LightweightFashionMNIST(nn.Module):
    def __init__(self):
        super(LightweightFashionMNIST, self).__init__()
        # Входное изображение: 1 x 28 x 28
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)   # -> 16 x 28 x 28
        self.pool  = nn.MaxPool2d(2, 2)                             # -> 16 x 14 x 14
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)    # -> 32 x 14 x 14
        # После второго pooling: 32 x 7 x 7
        self.fc1   = nn.Linear(32 * 7 * 7, 64)
        self.fc2   = nn.Linear(64, 10)  # 10 классов

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x