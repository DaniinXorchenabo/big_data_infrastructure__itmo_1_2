package com.example.datamart

import org.apache.spark.sql.types._

import com.typesafe.config.ConfigFactory
import org.apache.spark.sql.{SaveMode, SparkSession}

object DataMartApp {
  def main(args: Array[String]): Unit = {
    // Load configuration from environment or application.conf
    val mongoUri = sys.env("MONGO_URI")
    val neo4jUrl = sys.env("NEO4J_URL")
    val neo4jUser = sys.env("NEO4J_USER")
    val neo4jPass = sys.env("NEO4J_PASS")

    // Initialize SparkSession with MongoDB and Neo4j settings
    val spark = SparkSession.builder()
      .appName("DataMartApp")
      .config("spark.jars.packages", "org.neo4j:neo4j-connector-apache-spark_2.12:5.3.1_for_spark_3")
      .config("neo4j.url", neo4jUrl) // Замените на ваш адрес Neo4j
      .config("neo4j.authentication.basic.username", neo4jUser)
      .config("neo4j.authentication.basic.password", neo4jPass)
      .config("spark.mongodb.read.connection.uri", mongoUri)
      .config("spark.neo4j.bolt.url", neo4jUrl)
      .config("spark.neo4j.bolt.user", neo4jUser)
      .config("spark.neo4j.bolt.password", neo4jPass)
      .getOrCreate()


    val customSchema = StructType(Seq(
      StructField("_id", StringType, true),
      StructField("product_name", StringType, true),
      StructField("ingredients_n", IntegerType, nullable = true),
      StructField("ingredients_sweeteners_n", IntegerType, nullable = true),
      StructField("scans_n", IntegerType, nullable = true),
      StructField("additives_n", IntegerType, nullable = true),
    ))

    // Read raw data from MongoDB
    val rawDF = spark.read.format("mongodb").schema(customSchema).option("database", "off").option("collection", "products").option("uri", "mongodb://mongo:27017").option("sql.inferSchema.mapTypes.enabled", "true").option("sql.inferSchema.mapTypes.minimum.key.size", "10").load()

    // Data preprocessing: select and drop nulls
    val cleanDF = rawDF
      .select(
        rawDF("_id"),
        rawDF("product_name"),
        rawDF("ingredients_n"),
        rawDF("ingredients_sweeteners_n"),
        rawDF("scans_n"),
        rawDF("additives_n")
      )
      .na.drop()

    // Write cleaned data as Neo4j nodes labeled 'CleanedProduct'
    cleanDF.write
      .format("org.neo4j.spark.DataSource")
      .mode(SaveMode.Overwrite)
      .option("labels", "CleanedProduct")
      .option("node.keys", "_id")
      .save()

    spark.stop()
  }
}
