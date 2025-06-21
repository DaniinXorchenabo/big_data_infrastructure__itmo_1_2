import traceback
import os

os.environ["HOME"] = "/tmp"
os.environ["PYSPARK_PYTHON"] = "/opt/bitnami/python/bin/python3"
os.environ["PYSPARK_DRIVER_PYTHON"] = "/opt/bitnami/python/bin/python3"

os.environ["PYSPARK_SUBMIT_ARGS"] = f"""
--conf spark.executor.memory={os.environ['K8S_SPARK_EXECUTOR_MEMORY']}
--conf spark.executor.cores={os.environ['K8S_SPARK_EXECUTOR_CORES']}
pyspark-shell
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pyspark.sql import SparkSession, DataFrame
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

MONGO_USER = os.environ["K8S_MONGO_USER"]
MONGO_PASS = os.environ["K8S_MONGO_PASSWORD"]
MONGO_HOST = os.environ["K8S_MONGO_EXTERNAL_HOST"]
MONGO_PORT = os.environ["K8S_MONGO_EXTERNAL_PORT"]
MONGO_ADDR = f"{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"


# --- Обработчик фичей ---
def preprocess(df: DataFrame) -> DataFrame:
    selected = (
        df.select("_id", "product_name", "ingredients_n", "ingredients_sweeteners_n", "scans_n", "additives_n")
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
    return scaler.transform(assembled).select("_id", "product_name", "features")


# --- Pydantic-модели для JSON-ответа ---
class Features(BaseModel):
    _id: str
    id: str
    identify_param: str
    product_name: str
    features: List[float]


# Схема чтения из MongoDB
def get_custom_schema():
    return StructType([
        StructField("_id", StringType(), True),
        StructField("product_name", StringType(), True),
        StructField("ingredients_sweeteners_n", IntegerType(), True),
        StructField("ingredients_n", IntegerType(), True),
        StructField("additives_n", IntegerType(), True),
        StructField("scans_n", IntegerType(), True),
    ])


# 1) Инициализация SparkSession
spark = (
    SparkSession.builder
    .appName("DataMart-HTTP-Service")
    .master(os.environ['K8S_SPARK_MASTER_URL'])
    .config("spark.jars.ivy", "/tmp/.ivy2")
    .config("spark.executor.instances", os.environ['K8S_SPARK_EXECUTOR_INSTANCES'])
    .config("spark.executor.cores", os.environ['K8S_SPARK_EXECUTOR_CORES'])
    .config("spark.executor.memory", os.environ['K8S_SPARK_EXECUTOR_MEMORY'])

    .config("spark.submit.deployMode", "client")
    .config("spark.driver.memory", os.environ['K8S_SPARK_DRIVER_MEMORY'])  # драйверу тоже ограничим RAM, если нужно
    .config("spark.driver.host", os.environ['K8S_SPARK_DRIVER_HOST'])
    .config("spark.driver.bindAddress", os.environ['K8S_SPARK_DRIVER_BIND_ADDRESS'])
    .config("spark.driver.port", os.environ['K8S_SPARK_DRIVER_PORT'])
    .config("spark.blockManager.port", os.environ['K8S_SPARK_BLOCKMANAGER_PORT'])
    .config("spark.mongodb.read.connection.uri", f"mongodb://{MONGO_ADDR}")
    .config("spark.mongodb.write.connection.uri", f"mongodb://{MONGO_ADDR}")
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.3.0,"
                                   "com.redislabs:spark-redis_2.12:3.1.0,"
                                   "org.neo4j:neo4j-connector-apache-spark_2.12:5.3.1_for_spark_3")
    .config("spark.pyspark.python", os.environ["PYSPARK_PYTHON"])
    .config("spark.executorEnv.PYSPARK_PYTHON", os.environ["PYSPARK_DRIVER_PYTHON"])
    .getOrCreate()
)

# Инициализируем FastAPI
app = FastAPI(title="DataMart PyService")


@app.get("/preprocessed", response_model=List[Features])
async def get_preprocessed():
    try:
        # Читаем из MongoDB
        df = (
            spark.read.schema(get_custom_schema())
            .format("mongodb")
            .options(host=f"{MONGO_HOST}:{MONGO_PORT}", database="off", collection='products')
            .load()
        )
        # Препроцессинг
        result_df = preprocess(df)
        # Собираем результаты в Python
        rows = result_df.collect()
        output = [
            Features(_id=row["_id"], id=row["_id"],
                     identify_param=row["_id"],
                     product_name=row["product_name"],
                     features=row["features"].toArray().tolist())
            for row in rows
        ]
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) + "\n" + traceback.format_exc())

# Для запуска:
#   uvicorn this_module:app --host 0.0.0.0 --port 8080
