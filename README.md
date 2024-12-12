# Технологии программирования и обучения нейронных сетей ИТМО 1_1



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
```

7. Input your token
```bash
nano ./env/.env
```

8. Run docker image

In windows console:
```bash
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864  -p 0.0.0.0:8889:8888 -p 0.0.0.0:6006:6006 --rm -it --env-file ./env/.env -v .:/workspace/NN --mount type=bind,src=%cd%/docker/jupyter_config,dst=/root/.jupyter/   daniinxorchenabo/itmo_dl_labs-env:lighting-cu122-latest 
```

In linux console:
```bash
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864  -p 0.0.0.0:8889:8888 -p 0.0.0.0:6006:6006 --rm -it --env-file ./env/.env -v .:/workspace/NN --mount type=bind,src=$(PWD)/docker/jupyter_config,dst=/root/.jupyter/   daniinxorchenabo/itmo_dl_labs-env:lighting-cu122-latest 
```



