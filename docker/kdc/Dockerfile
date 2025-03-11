FROM debian:stable-slim

# Устанавливаем необходимые пакеты для работы KDC
RUN apt-get update && \
    apt-get install -y krb5-kdc krb5-admin-server && \
    rm -rf /var/lib/apt/lists/*

# Копируем конфигурационные файлы Kerberos
COPY ./krb5.conf /etc/krb5.conf
COPY ./kdc.conf /etc/krb5kdc/kdc.conf
COPY ./kadm5.acl /etc/krb5kdc/kadm5.acl

EXPOSE 88 749

# Для демонстрационных целей запускаем KDC в foreground
COPY ./init_kdc.sh /init_kdc.sh
RUN chmod +x /init_kdc.sh
CMD ["/init_kdc.sh"]
#CMD ["/usr/sbin/krb5kdc", "-n"]
