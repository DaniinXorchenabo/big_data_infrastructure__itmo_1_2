FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update  \
    && apt-get install -y \
    curl jq git build-essential libssl-dev libffi-dev python3 python3-venv python3-pip  libicu-dev

RUN useradd -m docker
# Получение GID сокета Docker и создание группы с этим GID
RUN DOCKER_GID=$(stat -c '%g' /var/run/docker.sock || echo 999) && \
    groupadd -g $DOCKER_GID docker_group && \
    usermod -aG docker_group docker
USER docker
WORKDIR /home/docker

RUN mkdir actions-runner  \
    && cd actions-runner  \
    && curl -o actions-runner-linux-x64-2.323.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.323.0/actions-runner-linux-x64-2.323.0.tar.gz \
    && echo "0dbc9bf5a58620fc52cb6cc0448abcca964a8d74b5f39773b7afcad9ab691e19  actions-runner-linux-x64-2.323.0.tar.gz" | shasum -a 256 -c \
    && tar xzf ./actions-runner-linux-x64-2.323.0.tar.gz


USER root


# Устанавливаем утилиты и lsb-release
RUN apt-get update \
 && apt-get install -y \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg2 \
      lsb-release \
 && mkdir -p /etc/apt/keyrings

# Импортируем GPG-ключ Docker в non-interactive режиме
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
      | gpg --batch --yes --no-tty --dearmor \
      -o /etc/apt/keyrings/docker.gpg

# Создаём корректный список источников для Docker
RUN printf "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\n" \
      | tee /etc/apt/sources.list.d/docker.list

# Обновляем индексы и устанавливаем Docker CLI и плагины
RUN apt-get update \
 && apt-get install -y \
      docker-ce-cli \
      containerd.io \
      docker-buildx-plugin \
      docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*


#USER docker
#
#
#
USER root
ADD start.sh /home/docker/actions-runner-scrpt/start.sh
RUN chmod +x /home/docker/actions-runner-scrpt/start.sh
RUN groupadd -f docker && usermod -aG docker docker &&  newgrp docker
USER docker
#USER root

ENTRYPOINT ["/home/docker/actions-runner-scrpt/start.sh"]


