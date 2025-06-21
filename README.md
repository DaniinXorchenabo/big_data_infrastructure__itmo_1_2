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
8. Init `vault` and add secrets (for more info, see `./docker/vault/init_vault.sh` or `./.github/workflows/cd-pipeline.yml`).

8.1. Init vault
```bash
docker-compose -f .\docker\docker-compose.yml --env-file .\env\.env  up -d --build --force-recreate vault
docker exec -it  vault mkdir -p /vault/data
docker exec -it  vault chown -R vault /vault/data
docker exec -it  vault vault operator init -format=json 
```
8.2. Add `root_token` and `unseal_keys` to /env/.env and  /env/.env

8.3. Add necessary secrets as environ variables
```bash
export DB_PORT =
export DB_LOGIN =
export DB_PASSWORD =
export JUPYTER_TOKEN =
export AI_WEIGHTS_REPO =
export AI_WEIGHTS_FILENAME =
export AI_WEIGHTS_REPO_FILENAME =
```

8.4. Add necessary secrets into `vault`
```bash
./docker/vault/init_variables.sh
```

8. Run docker image

Run main only `docker-compose` 
```bash
docker-compose -f .\docker\docker-compose.yml --env-file .\env\.env  up -d --build --force-recreate
```

Run main `docker-compose` with `gpu` (production usage)
```bash
docker-compose -f .\docker\docker-compose.yml -f .\docker\gpu.docker-compose.yml  --env-file .\env\.env  up -d --build --force-recreate 
```

Run  autotests 
```bash
docker-compose -f .\docker\docker-compose.yml -f .\docker\autotest.docker-compose.yml  --env-file .\env\unittests.env  up -d --build --force-recreate 
docker exec -it producer pytest -vv -c ./tests/pytest.ini
```

Run autotests with `gpu`
```bash
docker-compose -f .\docker\docker-compose.yml -f .\docker\autotest.docker-compose.yml  -f .\docker\gpu.docker-compose.yml --env-file .\env\unittests.env  up -d --build --force-recreate 
docker exec -it producer pytest -vv -c ./tests/pytest.ini
```


Run for developing in `jupyter notebooks` with `gpu`:
```bash
docker-compose -f .\docker\docker-compose.yml -f .\docker\gpu.docker-compose.yml -f .\docker\composes\gpu.dev.docker-compose.yml --env-file .\env\.env  up -d --build --force-recreate
```

Run for developing in `jupyter notebooks` without `gpu`:
```bash
docker-compose -f .\docker\docker-compose.yml  -f .\docker\composes\cpu.dev.docker-compose.yml --env-file .\env\.env  up -d --build --force-recreate                         ```
```



