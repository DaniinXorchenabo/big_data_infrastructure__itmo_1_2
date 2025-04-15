FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update  \
    && apt-get install -y \
    curl jq git build-essential libssl-dev libffi-dev python3 python3-venv python3-pip  libicu-dev

WORKDIR /home/docker

RUN mkdir actions-runner  \
    && cd actions-runner  \
    && curl -o actions-runner-linux-x64-2.323.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.323.0/actions-runner-linux-x64-2.323.0.tar.gz \
    && echo "0dbc9bf5a58620fc52cb6cc0448abcca964a8d74b5f39773b7afcad9ab691e19  actions-runner-linux-x64-2.323.0.tar.gz" | shasum -a 256 -c \
    && tar xzf ./actions-runner-linux-x64-2.323.0.tar.gz


COPY start.sh /home/docker/actions-runner/start.sh
RUN chmod +x /home/docker/actions-runner/start.sh
RUN useradd -m docker
USER docker

ENTRYPOINT ["/home/docker/actions-runner/start.sh"]


