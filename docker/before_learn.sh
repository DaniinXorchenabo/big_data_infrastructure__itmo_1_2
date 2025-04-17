#!/bin/bash

tensorboard --logdir_spec $(python ./docker/jupyter_config/get_tensorboard_logs_files.py)   --host 0.0.0.0 &
jupyter lab --allow-root --ip=0.0.0.0 --ServerApp.iopub_data_rate_limit=1.0e10 --ServerApp.rate_limit_window=10.0 --config=/root/.jupyter/jupyter_lab_config.py