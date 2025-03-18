#!/bin/bash

#docker-compose -f ./docker/docker-compose.yml --env-file ./env/.env  up vault  -d --force-recreate
#docker exec -it  vault /bin/sh
#mkdir -p /vault/data
#chown -R vault /vault/data
mkdir -p /vault/data
chown -R vault /vault/data &&
init_output=$( vault operator init -format=json)

if [ $? -ne 0 ]; then
  echo "Ошибка инициализации Vault"
  exit 1
fi

# Извлекаем unseal-ключи (массив) и root-токен с помощью jq
#unseal_keys=$(echo "$init_output" | jq -r '.unseal_keys_b64[]')  # unseal_keys_hex
readarray -t unseal_keys < <(echo "$init_output" | jq -r '.unseal_keys_b64[]')
root_token=$(echo "$init_output" | jq -r '.root_token')

# Сохраняем первые три unseal-ключа в переменные окружения
export VAULT_UNSEAL_KEY_1="${unseal_keys[0]}"
export VAULT_UNSEAL_KEY_2="${unseal_keys[1]}"
export VAULT_UNSEAL_KEY_3="${unseal_keys[2]}"
export VAULT_UNSEAL_KEY_4="${unseal_keys[3]}"
export VAULT_UNSEAL_KEY_5="${unseal_keys[4]}"
# При необходимости можно добавить дополнительные ключи
#sleep 10s
# Сохраняем root-токен
export VAULT_ROOT_TOKEN="$root_token"

echo "Инициализация Vault завершена. Ключи сохранены в переменные окружения:"
echo "VAULT_UNSEAL_KEY_1=$VAULT_UNSEAL_KEY_1"
echo "VAULT_UNSEAL_KEY_2=$VAULT_UNSEAL_KEY_2"
echo "VAULT_UNSEAL_KEY_3=$VAULT_UNSEAL_KEY_3"
echo "VAULT_ROOT_TOKEN=$VAULT_ROOT_TOKEN"

#sleep 2h
