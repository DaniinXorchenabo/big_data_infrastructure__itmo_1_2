import os
from functools import reduce

__all__ = []

deep = 3
ROOT_DIR = reduce(lambda x, _: os.path.split(x)[0], range(deep), __file__)

os.chdir(ROOT_DIR)

# WEIGHTS_DIR = os.path.join(ROOT_DIR, 'neural', 'weights', 'prod')
# MODEL_DIR = os.path.join(WEIGHTS_DIR, os.environ.get('AI_WEIGHTS_FILENAME'))
#
#
# fashion_mnist_lit_model_weights = os.path.join(WEIGHTS_DIR, 'fashion_MNIST_lite_2025_02_27__11_35_34_af5d8943-4cf8-4204-b7a3-f39e5a49e673-epoch=10-val_auroc=0.99.ckpt')