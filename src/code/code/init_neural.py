import numpy as np
import torch
from datetime import datetime
import adapters
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, \
    RobertaForSequenceClassification
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from torch.nn import functional as F
from torch import Tensor
from sklearn.metrics import mean_squared_error, accuracy_score, roc_auc_score, f1_score
from uuid import uuid4
import nlpaug.augmenter.word as naw
import random
from nltk.corpus import wordnet
import numpy as np
import random
from nltk.corpus import wordnet
from transformers import BertConfig
from adapters import AutoAdapterModel
from adapters import ConfigUnion, ParBnConfig, PrefixTuningConfig

from src.code.configs.config import DEVICE, ADAPTER_NAME
from src.code.configs.paths_config import WEIGHTS_DIR, MODEL_DIR

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


model_name = "distilbert-base-uncased"

tokenizer = AutoTokenizer.from_pretrained(
WEIGHTS_DIR
    # model_name,
    # problem_type="multi_label_classification",
    # cache_dir=os.path.join(WEIGHTS_DIR, 'pretrain')
)

model = AutoModelForSequenceClassification.from_pretrained(
MODEL_DIR,
    # model_name,
    num_labels=28,
    problem_type="multi_label_classification",
    # cache_dir=os.path.join(WEIGHTS_DIR, 'pretrain')
)

model = AutoAdapterModel.from_pretrained(
    model_name,
    config=model.config,
    # problem_type="multi_label_classification",
    # num_labels=28,
).to(DEVICE)

adapters.init(model)


config = ConfigUnion(
    PrefixTuningConfig(bottleneck_size=800),
    ParBnConfig(),
)
model.add_adapter(ADAPTER_NAME, config=config)