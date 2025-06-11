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

  val conf = ConfigFactory.load()
  val mongoUri = sys.env.getOrElse("MONGO_URI", conf.getString("datamart.source.mongoUri"))

  // инициализируем Spark один раз
  val spark = SparkSession.builder()
    .appName("DataMart HTTP Service")
    .config("spark.mongodb.read.connection.uri", mongoUri)
    .getOrCreate()

  import JsonProtocol._

  def loadAndPreprocess(): Future[Seq[Features]] = Future {
    val raw = spark.read.format("mongodb")
      .option("uri", mongoUri)
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
