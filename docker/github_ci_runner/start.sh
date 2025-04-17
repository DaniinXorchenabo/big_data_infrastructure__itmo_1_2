#!/bin/bash
set -e

cd /home/docker/actions-runner

# Получение токена регистрации
REG_TOKEN=$(curl -sX POST -H "Authorization: token ${ACCESS_TOKEN}" \
    https://api.github.com/repos/${REPO}/actions/runners/registration-token | jq -r .token)

# Конфигурация runner
./config.sh --url https://github.com/${REPO} --token ${ACCESS_TOKEN}

# Запуск runner
./run.sh
