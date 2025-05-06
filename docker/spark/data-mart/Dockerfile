FROM bitnami/spark:3.5.1


USER root

# 1. Обновляем APT, устанавливаем утилиты HTTPS-репозиториев
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg && \
    curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" \
      | gpg --dearmor \
      | tee /usr/share/keyrings/sbt-keyring.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/sbt-keyring.gpg] \
      https://repo.scala-sbt.org/scalasbt/debian all main" \
      | tee /etc/apt/sources.list.d/sbt.list && \
    apt-get update && \
    apt-get install -y sbt && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./build.sbt .
COPY project/ ./project/
COPY ./application.conf ./src/main/resources/application.conf
COPY ./DataMartApp.scala ./src/main/scala/com/example/datamart/DataMartApp.scala

COPY ./Preprocessing.scala ./srcmain/scala/com/example/datamart/transform/Preprocessing.scala

# Сборка fat-jar
RUN sbt assembly

# Запуск ETL
# Правильная exec-форма ENTRYPOINT:
# весь spark-submit и его параметры указываем единой JSON-массивной строкой
ENTRYPOINT ["spark-submit", \
    "--packages", \
    "org.neo4j:neo4j-connector-apache-spark_2.12:5.3.1_for_spark_3,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0", \
    "--class", \
    "com.example.datamart.DataMartApp", \
    "/app/target/scala-2.12/datamart-assembly-0.1.jar"]