#!/bin/bash
set -e

echo "AAAAAA"

export RUNNER_ALLOW_RUNASROOT=1
DOCKER_GID=$(stat -c '%g' /var/run/docker.sock || echo 999)

# Создание группы с GID сокета Docker, если она не существует
if ! getent group docker >/dev/null; then
  groupadd -g "$DOCKER_GID" docker
fi

# Добавление пользователя 'docker' в группу 'docker'
usermod -aG docker docker


# Параметры: ACCESS_TOKEN и REPO должны быть заданы в переменных окружения
if [[ -z "$ACCESS_TOKEN" || -z "$REPO" ]]; then
  echo "Ошибка: переменные окружения ACCESS_TOKEN и REPO должны быть заданы."
  exit 1
fi
echo "AAAAAA"
cd /home/docker/actions-runner

# Проверка наличия конфигурации runner
if  [[ -f "/home/docker/actions-runner/.runner" ]] ; then
  echo "Runner уже зарегистрирован. Запускаем..."

else

  echo "Runner -- не зарегистрирован. Выполняем регистрацию..."

  # Получение токена регистрации
#  REG_TOKEN=$(curl -sX POST \
#    -H "Authorization: token $ACCESS_TOKEN" \
#    -H "Accept: application/vnd.github+json" \
#    https://api.github.com/repos/$REPO/actions/runners/registration-token | jq -r .token)

#REG_TOKEN=$(curl -sX POST -H "Authorization: token ${ACCESS_TOKEN}" \
#    https://api.github.com/repos/${REPO}/actions/runners/registration-token | jq -r .token)

#  if [[ -z "$REG_TOKEN" || "$REG_TOKEN" == "null" ]]; then
#    echo "Ошибка: не удалось получить токен регистрации."
#    exit 1
#  fi
  echo "$REG_TOKEN"
  ./config.sh --url https://github.com/$REPO \
              --token "$ACCESS_TOKEN" \
              --unattended \
              --name "$(hostname)" \
              --labels self-hosted,linux \
              --replace


#   Конфигурация runner
#  ./config.sh --url https://github.com/${REPO} --token ${ACCESS_TOKEN}
#
#   Регистрация runner
#  ./config.sh --url https://github.com/$REPO \
#              --token "$REG_TOKEN" \
#              --unattended \
#              --name "$(hostname)" \
#              --labels self-hosted,linux \
#              --replace
fi



# Запуск runner
./run.sh
