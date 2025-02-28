# Инфраструктура больших данных ИТМО 1_1



## Run and build

1. Copy [entrypoint.d](https://gitlab.com/nvidia/container-images/cuda/-/tree/master/entrypoint.d) to `<project_root>/docker/source`
2. Copy [NGC-DL-CONTAINER-LICENSE](https://gitlab.com/nvidia/container-images/cuda/-/blob/master/NGC-DL-CONTAINER-LICENSE) to `<project_root>/docker/source`
3. Copy [nvidia_entrypoint.sh](https://gitlab.com/nvidia/container-images/cuda/-/blob/master/nvidia_entrypoint.sh) to `<project_root>/docker/source`
4. (Optional) Enable `docker` [Buildkit](https://docs.docker.com/build/buildkit/#:~:text=To%20use%20Docker%20BuildKit%20by,the%20following%20to%20the%20file)

5.
```bash
docker build -f  ./docker/lighting.Dockerfile --build-arg REQUIREMENTS_FILE=cu_12_2.txt . -t daniinxorchenabo/itmo_dl_labs-env:lighting-cu122-latest
```

6.
```bash
cp ./env/example.env ./env/.env
cp ./env/example.env ./env/unittests.env
```

7. Input your token and other empty fields
```bash
nano ./env/.env
nano ./env/unittests.env
```

8. Run docker image

Run for developing in jupyter notebooks:
```bash
docker-compose -f .\docker\dev.docker-compose.yml --env-file .\env\.env  up -d --build
```

Run for testing
```bash
docker-compose -f .\docker\dev.docker-compose.yml -f .\docker\test.docker-compose.yml --env-file .\env\unittests.env  up  --no-deps unittests --build
```

Run for production usage
```bash
docker-compose -f .\docker\dev.docker-compose.yml -f .\docker\prod.docker-compose.yml --env-file .\env\.env  up -d  --build
```

Or your run dockerfile only (deprecated)

* In windows console:
```bash
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864  --memory="40g" --memory-swap="60g" -p 0.0.0.0:8889:8888 -p 0.0.0.0:6006:6006 -p 0.0.0.0:6007:6007 --rm -it --env-file ./env/.env -v .:/workspace/NN --mount type=bind,src=%cd%/docker/jupyter_config,dst=/root/.jupyter/  --mount type=bind,src=%cd%/neural/datasets/fiftyone/,dst=/root/fiftyone/   daniinxorchenabo/itmo_dl_labs-env:lighting-cu122-latest ./docker/before_learn.sh
```

* In linux console:
```bash
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864  --memory="40g" --memory-swap="60g"  -p 0.0.0.0:8889:8888 -p 0.0.0.0:6006:6006 -p 0.0.0.0:6007:6007 --rm -it --env-file ./env/.env -v .:/workspace/NN --mount type=bind,src=$(PWD)/docker/jupyter_config,dst=/root/.jupyter/   daniinxorchenabo/itmo_dl_labs-env:lighting-cu122-latest ./docker/before_learn.sh
```



