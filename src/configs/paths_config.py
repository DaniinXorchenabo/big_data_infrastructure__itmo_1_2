import os
from functools import reduce

__all__ = []

deep = 3
ROOT_DIR = reduce(lambda x, _: os.path.split(x)[0], range(deep), __file__)

os.chdir(ROOT_DIR)
