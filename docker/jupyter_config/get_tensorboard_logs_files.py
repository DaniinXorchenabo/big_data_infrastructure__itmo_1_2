import os
from os.path import join, split, dirname, isdir
from functools import reduce
# from config.constants import ROOT_DIR

_FILE_NESTED_LEVEL = 2
ROOT_DIR = reduce(lambda i, _: split(i)[0], range(_FILE_NESTED_LEVEL), dirname(__file__))
LOGS_DIR = join(ROOT_DIR, 'neural', 'logs')
RAY_DIR = join(ROOT_DIR, 'neural', "tmp", 'ray')

if __name__ == "__main__":
    if isdir(LOGS_DIR):
        train_folders = [
            f"name_{ind}:{join(LOGS_DIR, f)}"
            for ind, f in enumerate(os.listdir(LOGS_DIR))
            if os.path.isdir(join(LOGS_DIR, f))
        ] + [f'base_log_dir:{LOGS_DIR}']
    else:
        train_folders = []

    if isdir(RAY_DIR):
        tune_folders = [
            f"{cl_name}_{full_path3}:{join(full_path, full_path2, full_path3, 'driver_artifacts')}"
            for full_path, cl_name in
            [
                [join(RAY_DIR, f, f2, 'artifacts'), f]
                for f in os.listdir(RAY_DIR)
                if os.path.isdir(join(RAY_DIR, f))
                for f2 in os.listdir(join(RAY_DIR, f))
                if os.path.isdir(join(RAY_DIR, f, f2, 'artifacts'))
            ]
            for full_path2 in os.listdir(full_path)
            if os.path.isdir(join(full_path, full_path2))
            for full_path3 in os.listdir(join(full_path, full_path2))
            if os.path.isdir(join(full_path, full_path2, full_path3, "driver_artifacts"))
        ]
    else:
        tune_folders = []
    print(*tune_folders, *train_folders, sep=',')

