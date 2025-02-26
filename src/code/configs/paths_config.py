import os
from functools import reduce

deep = 4
ROOT_DIR = reduce(lambda x, _: os.path.split(x)[0], range(deep), __file__)

os.chdir(ROOT_DIR)

WEIGHTS_DIR = os.path.join(ROOT_DIR, 'neural', 'weights', 'prod')
MODEL_DIR = os.path.join(WEIGHTS_DIR, os.environ.get('AI_WEIGHTS_FILENAME'))
