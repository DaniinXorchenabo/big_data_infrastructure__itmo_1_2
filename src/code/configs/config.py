import torch

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
transferlearning_type = 'mam'
ADAPTER_NAME = f"{transferlearning_type}_adapter"