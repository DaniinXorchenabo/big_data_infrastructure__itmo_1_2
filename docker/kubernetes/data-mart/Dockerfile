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
COPY ./application.conf ./src/main/resources/application.conf
COPY ./HttpDataMartApp.scala ./src/main/scala/com/example/datamart/HttpDataMartApp.scala
COPY ./Preprocessing.scala ./src/main/scala/com/example/datamart/transform/Preprocessing.scala

# Собираем fat-jar с akka-http и spark
RUN sbt assembly
ENTRYPOINT [ \
    "spark-submit", \
    "--master", "spark://host.docker.internal:30077", \
    "--deploy-mode", "client", \
    "--conf", "spark.kubernetes.container.image=bitnami/spark:3.5.6", \
    "--conf", "spark.kubernetes.namespace=default", \
    "--conf", "spark.kubernetes.authenticate.driver.serviceAccountName=spark", \
    "--conf", "spark.executor.instances=1", \
    "--conf", "spark.executor.cores=1", \
    "--conf", "spark.executor.memory=1g", \
    "--conf", "spark.driver.memory=1g", \
    "--conf", "spark.driver.host=host.docker.internal", \
    "--conf", "spark.driver.bindAddress=0.0.0.0", \
    "--conf", "spark.driver.port=31555", \
    "--conf", "spark.blockManager.port=31556", \
    "--conf", "spark.jars.ivy=/tmp/.ivy2", \
    "--conf", "spark.jars.packages=org.mongodb.spark:mongo-spark-connector_2.12:10.3.0,com.redislabs:spark-redis_2.12:3.1.0,org.neo4j:neo4j-connector-apache-spark_2.12:5.3.1_for_spark_3", \
    "--conf", "spark.mongodb.read.connection.uri=mongodb://admin:password@host.docker.internal:30717", \
    "--conf", "spark.mongodb.write.connection.uri=mongodb://admin:password@host.docker.internal:30717", \
    "--conf", "spark.redis.host=host.docker.internal", \
    "--conf", "spark.redis.port=30079", \
    "--conf", "spark.redis.db=0", \
    "--conf", "spark.neo4j.bolt.url=bolt://host.docker.internal:30787", \
    "--conf", "spark.neo4j.bolt.user=neo4j", \
    "--conf", "spark.neo4j.bolt.password=password", \
    "--conf", "neo4j.url=bolt://host.docker.internal:30787", \
    "--conf", "neo4j.authentication.basic.username=neo4j", \
    "--conf", "neo4j.authentication.basic.password=password", \
    "--packages", \
    "org.neo4j:neo4j-connector-apache-spark_2.12:5.3.1_for_spark_3,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0", \
     "--class", "com.example.datamart.HttpDataMartApp",\
    "/app/target/scala-2.12/datamart-assembly-0.1.jar" \
     ]

#ENTRYPOINT ["java", "-jar", "/app/target/scala-2.12/datamart-assembly-0.1.jar"]
#java -jar /app/target/scala-2.12/datamart-assembly-0.1.jar
#ENTRYPOINT ["java", "-cp", "/app/target/scala-2.12/datamart-assembly-0.1.jar", "com.example.datamart.HttpDataMartApp"]

#java -cp /app/target/scala-2.12/datamart-assembly-0.1.jar com.example.datamart.HttpDataMartApp