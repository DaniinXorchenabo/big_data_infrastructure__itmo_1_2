package com.example.datamart

import akka.actor.ActorSystem
import akka.http.scaladsl.Http
import akka.http.scaladsl.model._
import akka.http.scaladsl.server.Directives._
import akka.stream.Materializer
import com.example.datamart.transform.Preprocessing
import com.typesafe.config.ConfigFactory
import org.apache.spark.sql.{SparkSession, DataFrame}
import spray.json._
//

import scala.concurrent.{ExecutionContext, Future}

// JSON-маршаллер для Vector[Float]
case class Features(features: Seq[Double])
object JsonProtocol extends DefaultJsonProtocol {
  implicit val featuresFormat = jsonFormat1(Features)
}

object HttpDataMartApp extends App {
  implicit val system: ActorSystem = ActorSystem("data-mart-system")
  implicit val ec: ExecutionContext = system.dispatcher
  implicit val mat: Materializer  = Materializer(system)
  import JsonProtocol._
  val conf = ConfigFactory.load()
  val mongoUri = "mongodb://admin:password@host.docker.internal:30717"
  // инициализируем Spark один раз

  val spark = SparkSession.builder()
  .appName("DataMart-HTTP-Service")
  .master("spark://host.docker.internal:30077")
  .config("spark.kubernetes.container.image", "bitnami/spark:latest")
  .config("spark.kubernetes.namespace", "default")
  .config("spark.kubernetes.authenticate.driver.serviceAccountName", "spark")
  .config("spark.executor.instances", "1")
  .config("spark.executor.cores", "1")
  .config("spark.executor.memory", "1g")
  .config("spark.driver.memory", "1g")
  .config("spark.driver.host", "host.docker.internal")
  .config("spark.driver.bindAddress", "0.0.0.0")
  //.config("spark.driver.port", "31555")
  //.config("spark.blockManager.port", "31556")
  .config("spark.jars.ivy", "/tmp/.ivy2")

  // JAR-зависимости (через spark.jars.packages)
  .config(
    "spark.jars.packages",
    Seq(
      "org.mongodb.spark:mongo-spark-connector_2.12:10.3.0",
      "com.redislabs:spark-redis_2.12:3.1.0",
      "org.neo4j:neo4j-connector-apache-spark_2.12:5.3.1_for_spark_3"
    ).mkString(",")
  )

  // MongoDB
  .config("spark.mongodb.read.connection.uri", "mongodb://admin:password@host.docker.internal:30717")
  .config("spark.mongodb.write.connection.uri", "mongodb://admin:password@host.docker.internal:30717")
  .config("spark.mongodb.read.connection.url", "mongodb://admin:password@host.docker.internal:30717")
  .config("spark.mongodb.write.connection.url", "mongodb://admin:password@host.docker.internal:30717")
  // Redis
  .config("spark.redis.host", "host.docker.internal")
  .config("spark.redis.port", "30079")
  .config("spark.redis.db", "0")

  // Neo4j
  .config("spark.neo4j.bolt.url", "bolt://host.docker.internal:30787")
  .config("spark.neo4j.bolt.user", "neo4j")
  .config("spark.neo4j.bolt.password", "password")
  .config("neo4j.url", "bolt://host.docker.internal:30787")
  .config("neo4j.authentication.basic.username", "neo4j")
  .config("neo4j.authentication.basic.password", "password")

  .getOrCreate()


  def loadAndPreprocess(): Future[Seq[Features]] = Future {
    println(s"[DataMart] Spark master = ${spark.sparkContext.master}")
    // println(s"[DataMart] Mongo URI   = ${mongoUri}")
    val mongoUri = spark.sparkContext.getConf.get("spark.mongodb.read.connection.uri", "mongodb://localhost:27017")
                                      // ↑ второй аргумент — дефолт, если ключ не найден
    println(s"Mongo URI из SparkConf = $mongoUri")
    val raw = spark.read.format("mongodb")
       .option("uri", "mongodb://admin:password@host.docker.internal:30717")
      .option("database", "off")
      .option("collection", "products")
      .load()

    val processed: DataFrame = Preprocessing.transform(raw)
    // преобразуем Spark DataFrame в Seq[Features]
    processed.collect().map { row =>
      val vector = row.getAs[org.apache.spark.ml.linalg.Vector]("features")
      Features(vector.toArray.map(_.toDouble).toSeq)
    }
  }
  //import JsonProtocol._
  val route =
    path("preprocessed") {
      get {
        onComplete(loadAndPreprocess()) {
          case scala.util.Success(data) =>
            complete(HttpEntity(
              ContentTypes.`application/json`,
              data.toJson.prettyPrint
            ))
          case scala.util.Failure(ex) =>
            complete(StatusCodes.InternalServerError, s"Error: ${ex.getMessage}")
        }
      }
    }

  val bindingFuture = Http().newServerAt("0.0.0.0", 12080).bind(route)
  println("DataMart HTTP service running at http://0.0.0.0:12080/")
}
