import traceback
import os
os.environ["HOME"] = "/tmp"
os.environ["PYSPARK_SUBMIT_ARGS"] = f"""
--conf spark.executor.memory=1G
--conf spark.executor.cores=1
pyspark-shell
"""
os.environ["PYSPARK_PYTHON"] = "/opt/bitnami/python/bin/python3"
os.environ["PYSPARK_DRIVER_PYTHON"] = "/opt/bitnami/python/bin/python3"
MONGO_USER = 'admin'  # os.environ["MONGO_USER"]
MONGO_PASS = 'password'  # os.environ["MONGO_PASSWORD"]
MONGO_HOST = "host.docker.internal"
MONGO_PORT = "30717"
MONGO_ADDR = f"{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyspark.sql import SparkSession, DataFrame
from pyspark.ml.feature import VectorAssembler, StandardScaler
from typing import List

from pyspark.sql import SparkSession
from pyspark.sql.types import (StructType, StructField,
                               StringType, IntegerType, MapType,
                               DoubleType
                               )


# --- Обработчик фичей (аналог Scala Preprocessing) ---
def preprocess(df: DataFrame) -> DataFrame:
    selected = (
        df.select("ingredients_n", "ingredients_sweeteners_n", "scans_n", "additives_n")
          .na.drop()
    )
    assembler = VectorAssembler(
        inputCols=["ingredients_n", "ingredients_sweeteners_n", "scans_n", "additives_n"],
        outputCol="features_assembled"
    )
    assembled = assembler.transform(selected)
    scaler = StandardScaler(
        inputCol="features_assembled",
        outputCol="features"
    ).fit(assembled)
    return scaler.transform(assembled).select("features")

# --- Pydantic-модель для JSON-ответа ---
class Features(BaseModel):
    features: List[float]



custom_schema = StructType([
    StructField("_id", StringType(), True),
    StructField("product_name", StringType(), True),
# StructField("nutriments", MapType(StringType(), StringType()), True),
#     # Если есть другие поля, укажите их типы.
#     StructField("quantity", StringType(), True),
     StructField("ingredients_sweeteners_n", IntegerType(), True),
#      StructField("ingredients_percent_analysis", IntegerType(), True),
#      StructField("ingredients_non_nutritive_sweeteners_n", IntegerType(), True),
     StructField("ingredients_n", IntegerType(), True),
#     StructField("ingredients_from_palm_oil_n", IntegerType(), True),
#     StructField("ingredients_from_or_that_may_be_from_palm_oil_n", IntegerType(), True),
    StructField("additives_n", IntegerType(), True),
#     StructField("unique_scans_n", IntegerType(), True),
    StructField("scans_n", IntegerType(), True),
#     StructField("rev", IntegerType(), True),
#     StructField("popularity_key", IntegerType(), True),
#     StructField("packagings_n", IntegerType(), True),
#     StructField("packagings_complete", IntegerType(), True),
#     StructField("nutrition_score_warning_no_fiber", IntegerType(), True),
#     StructField("nutrition_score_warning_fruits_vegetables_nuts_estimate", IntegerType(), True),
#     StructField("nutrition_score_beverage", IntegerType(), True),
#     StructField("nutriscore_score_opposite", IntegerType(), True),
#     StructField("nutriscore_score", IntegerType(), True),
#     StructField("environmental_score_score", IntegerType(), True),
#     StructField("completeness", DoubleType(), True),
#     StructField("complete", IntegerType(), True),
#
#     StructField("energy_100g", IntegerType(), True),
#     StructField("proteins_100g", IntegerType(), True),
#     StructField("carbohydrates_100g", IntegerType(), True),
#     StructField("fat_100g", IntegerType(), True),
#     StructField("sugars_100g", IntegerType(), True),
#     StructField("saturated-fat_100g", IntegerType(), True),
#     StructField("salt_100g", IntegerType(), True),
#     StructField("sodium_100g", IntegerType(), True),

])

# 1) Создаём SparkSession, указываем master как spark://<имя-сервиса>:7077
#    При работе внутри Pod’а Kubernetes автоматически резолвит "spark-master" в его ClusterIP.
spark = (
    SparkSession.builder
        .appName("DataMart-HTTP-Service")
        # .master("spark://kayvan-release-spark-master-0:7077")
        .master("spark://host.docker.internal:30077")
        .config("spark.jars.ivy", "/tmp/.ivy2")  # укажи директорию вручную
        .config("spark.executor.instances", "1")      # сколько Executors запустить
        .config("spark.executor.cores", "1")          # по одному CPU‐ядру
        .config("spark.executor.memory", "1g")      # по 512 МБ памяти
        .config("spark.driver.memory", "1g")        # драйверу тоже ограничим RAM, если нужно

        .config("spark.submit.deployMode", "client")
        .config("spark.driver.bindAddress",  "0.0.0.0")
        # .config("spark.driver.port",         "45555")
        # .config("spark.blockManager.port",   "45556")
        .config("spark.driver.host", "host.docker.internal")

        .config("spark.driver.port",         "31555")
        .config("spark.blockManager.port",   "31556")
        .config("spark.mongodb.read.connection.uri", f"mongodb://{MONGO_ADDR}")
        .config("spark.mongodb.write.connection.uri", f"mongodb://{MONGO_ADDR}")
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.3.0,"
                                       "com.redislabs:spark-redis_2.12:3.1.0,"
                                       "org.neo4j:neo4j-connector-apache-spark_2.12:5.3.1_for_spark_3")
        .config("spark.pyspark.python", "/opt/bitnami/python/bin/python3")              # путь к python3 внутри контейнера
        .config("spark.executorEnv.PYSPARK_PYTHON", "/opt/bitnami/python/bin/python3")  # тоже самое для среды executor’а
        .getOrCreate()
)



# --- Инициализируем FastAPI ---
app = FastAPI(title="DataMart PyService")

@app.get("/preprocessed", response_model=List[Features])
async def get_preprocessed():
    try:
        # читаем из Mongo
        df = (
            spark.read.schema(custom_schema)
            .format("mongodb")
            .options(host=f"{MONGO_HOST}:{MONGO_PORT}", database="off", collection='products')
            .load()
        )
        # обрабатываем
        result_df = preprocess(df)
        # собираем в Python-список
        rows = result_df.collect()
        features_list = [
            Features(features=row["features"].toArray().tolist())
            for row in rows
        ]
        return features_list




    except Exception as e:
        raise HTTPException(status_code=500, detail=str(str(e) + "\n\n" + str(traceback.format_exc())))

# Для запуска:
#   uvicorn this_module:app --host 0.0.0.0 --port 8080
