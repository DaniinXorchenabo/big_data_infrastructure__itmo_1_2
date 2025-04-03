#!/bin/sh

export $(cat ./env/.env | xargs) && rails c

# Проверка состояния Vault
seal_status=$(docker exec -i  vault vault status -format=json | jq -r '.sealed')

if [[ "$seal_status" == "true" ]]; then
    echo "Vault запечатан. Начинаем процесс разблокировки..."
    docker exec -i  vault vault operator unseal "$VAULT_UNSEAL_KEY_1"
    docker exec -i  vault vault operator unseal "$VAULT_UNSEAL_KEY_2"
    docker exec -i  vault vault operator unseal "$VAULT_UNSEAL_KEY_3"
fi
echo "Vault уже разблокирован."

#export VAULT_SECRETS_PATH=something
#export VAULT_SECRETS_NAME=any

#export DB_PORT =
#export DB_LOGIN =
#export DB_PASSWORD =
#export JUPYTER_TOKEN =
#export AI_WEIGHTS_REPO =
#export AI_WEIGHTS_FILENAME =
#export AI_WEIGHTS_REPO_FILENAME =

docker exec -i  vault vault login $VAULT_ROOT_TOKEN

#docker exec -i  vault vault secrets enable -path="$VAULT_SECRETS_PATH" kv
#docker exec -i  vault vault secrets enable -path="$VAULT_SECRETS_PATH/$VAULT_SECRETS_NAME "kv
docker exec -i  vault vault secrets enable -path="${VAULT_SECRETS_PATH}/data/${VAULT_SECRETS_NAME}" kv

docker exec -i  vault vault kv put "${VAULT_SECRETS_PATH}/data/${VAULT_SECRETS_NAME}/DB_PORT" key="$DB_PORT"
docker exec -i  vault vault kv put "${VAULT_SECRETS_PATH}/data/${VAULT_SECRETS_NAME}/DB_LOGIN" key="$DB_LOGIN"
docker exec -i  vault vault kv put "${VAULT_SECRETS_PATH}/data/${VAULT_SECRETS_NAME}/DB_PASSWORD" key="$DB_PASSWORD"
docker exec -i  vault vault kv put "${VAULT_SECRETS_PATH}/data/${VAULT_SECRETS_NAME}/JUPYTER_TOKEN" key="$JUPYTER_TOKEN"
docker exec -i  vault vault kv put "${VAULT_SECRETS_PATH}/data/${VAULT_SECRETS_NAME}/AI_WEIGHTS_REPO" key="$AI_WEIGHTS_REPO"
docker exec -i  vault vault kv put "${VAULT_SECRETS_PATH}/data/${VAULT_SECRETS_NAME}/AI_WEIGHTS_FILENAME" key="$AI_WEIGHTS_FILENAME"
docker exec -i  vault vault kv put "${VAULT_SECRETS_PATH}/data/${VAULT_SECRETS_NAME}/AI_WEIGHTS_REPO_FILENAME" key="$AI_WEIGHTS_REPO_FILENAME"

sleep 2h