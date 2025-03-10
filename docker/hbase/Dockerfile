FROM harisekhon/hbase:latest

# Удаляем репозиторий edge/community, чтобы избежать ошибки "UNTRUSTED signature"
RUN sed -i '/edge\/community/d' /etc/apk/repositories  \
    && apk update \
    && apk add --no-cache krb5 openssh

# Копируем защищённую конфигурацию HBase
COPY ./conf/hbase-site.xml /opt/hbase/conf/hbase-site.xml

# Копируем конфигурационный файл Kerberos для клиента HBase
COPY ./kerberos/krb5.conf /etc/krb5.conf

# Если базовый образ использует Alpine, убедимся, что необходимые утилиты установлены.
# (Если потребуется, можно установить пакеты через apk или использовать другой базовый образ.)

# Копируем файлы конфигурации
COPY ./conf/hbase-site.xml /opt/hbase/conf/hbase-site.xml
COPY ./conf/hbase-env.sh /opt/hbase/conf/hbase-env.sh

# Делаем скрипт hbase-env.sh исполняемым (если требуется)
RUN chmod +x /opt/hbase/conf/hbase-env.sh

# Открываем нужные порты (хотя docker-compose их уже пробрасывает)
EXPOSE 16010 16020

# Переопределяем ENTRYPOINT, чтобы не мешало нашему CMD
ENTRYPOINT []
# Команда для запуска HBase в foreground.
# Запускаем HBase и затем переходим в режим tail логов мастера, чтобы контейнер не завершался.
CMD ["/bin/sh", "-c", "/opt/hbase/bin/start-hbase.sh && tail -F /hbase/logs/hbase--master-*.log"]
