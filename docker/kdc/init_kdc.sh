#!/bin/bash
set -e

# Параметры realm и пароли – настройте по необходимости
REALM="EXAMPLE.COM"
MASTER_PASSWORD="masterpassword"
ADMIN_PRINCIPAL="admin/admin"
ADMIN_PASSWORD="adminpassword"
HBASE_PRINCIPAL="hbase/$(hostname -f)@$REALM"
KEYTAB_PATH="/etc/krb5kdc/hbase.keytab"
KEYTAB_PATH2="/etc/krb5kdc/hbase-master.keytab"
KEYTAB_PATH3="/etc/krb5kdc/hbase-regionserver.keytab"
KDC_DB="/var/kerberos/krb5kdc/principal"

# Проверка, существует ли уже база данных KDC
if [ -f "$KDC_DB" ]; then
    echo "KDC database already exists. Skipping initialization."
else
    echo "Initializing KDC database for realm $REALM..."
    kdb5_util create -s -r "$REALM" -P "$MASTER_PASSWORD"

    echo "Creating admin principal ($ADMIN_PRINCIPAL)..."
    kadmin.local -q "addprinc -pw $ADMIN_PASSWORD $ADMIN_PRINCIPAL"

    echo "Creating HBase principal ($HBASE_PRINCIPAL)..."
    kadmin.local -q "addprinc -randkey $HBASE_PRINCIPAL"
    kadmin.local -q "addprinc -randkey $HBASE_PRINCIPAL"

    echo "Exporting keytab for HBase principal to $KEYTAB_PATH..."
    kadmin.local -q "ktadd -k $KEYTAB_PATH $HBASE_PRINCIPAL"
    kadmin.local -q "ktadd -k $KEYTAB_PATH2 $HBASE_PRINCIPAL"
    kadmin.local -q "ktadd -k $KEYTAB_PATH3 $HBASE_PRINCIPAL"


fi

echo "Starting KDC in foreground..."
exec /usr/sbin/krb5kdc -n
