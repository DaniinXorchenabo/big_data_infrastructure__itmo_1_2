FROM bitnami/spark:3.5.6

USER root
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
    rm -rf /var/lib/apt/lists/* \

RUN mkdir /app

WORKDIR /app
COPY build.sbt .
COPY ./project/ project/
COPY HttpDataMartApp.scala /src/main/scala/com/example/datamart/HttpDataMartApp.scala

# Собираем fat-jar с akka-http и spark
RUN sbt assembly

#ENTRYPOINT ["java", "-jar", "/app/target/scala-2.12/datamart-assembly-0.1.jar"]
java -jar /app/target/scala-2.12/datamart-assembly-0.1.jar

