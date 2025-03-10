#!/bin/sh
# Указываем, что HBase должен управлять ZooKeeper (встроенный режим)
#export HBASE_MANAGES_ZK=true
# Устанавливаем режим standalone
#export HBASE_CLUSTER_DISTRIBUTED=false
#export HBASE_MANAGES_ZOOKEEPER=true

export HBASE_MANAGES_ZK=false
export HBASE_CLUSTER_DISTRIBUTED=true
export HBASE_MANAGES_ZOOKEEPER=false
# Указываем путь к файлу конфигурации Kerberos (при условии, что он смонтирован или доступен в контейнере)
export JAVA_OPTS="$JAVA_OPTS -Djava.security.krb5.conf=/etc/krb5.conf"
# Пути к keytab-файлам для HBase (обратите внимание на путь внутри контейнера)
export HBASE_MASTER_KEYTAB=/opt/hbase/kerberos/hbase-master.keytab
export HBASE_REGIONSERVER_KEYTAB=/opt/hbase/kerberos/hbase-regionserver.keytab
# Параметры для безопасности Kerberos (при необходимости добавьте переменные для путей к keytab и т.п.)
# Пример:
# export HBASE_MASTER_KEYTAB=/opt/hbase/kerberos/hbase-master.keytab
# export HBASE_REGIONSERVER_KEYTAB=/opt/hbase/kerberos/hbase-regionserver.keytab

# Можно задать и другие переменные окружения по необходимости
