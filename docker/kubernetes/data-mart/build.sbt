import sbt._
import Keys._
import sbtassembly.AssemblyPlugin.autoImport._

name := "data-mart"
version := "0.1"
scalaVersion := "2.12.17"

// Зависимости вашего проекта
libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-sql" % "3.5.6" % "provided",
  "org.mongodb.spark" %% "mongo-spark-connector" % "10.3.0" % "provided",
  "org.neo4j" % "neo4j-connector-apache-spark_2.12" % "5.3.1_for_spark_3" % "provided",
  "com.typesafe" % "config" % "1.4.2"
)


// Указываем главный класс для манифеста
assembly / mainClass := Some("com.example.datamart.HttpDataMartApp")


// Настройка sbt-assembly
assembly / assemblyJarName := "datamart-assembly-0.1.jar"

// Стратегия слияния дублирующихся файлов
assembly / assemblyMergeStrategy := {
  case PathList("META-INF", xs @ _*) =>
    // Отбрасываем все мета-файлы, кроме сервисов
    xs.map(_.toLowerCase) match {
      case ("manifest.mf" :: Nil)    => MergeStrategy.discard
      case ("index.list" :: Nil)     => MergeStrategy.discard
      case ("dependencies" :: Nil)   => MergeStrategy.discard
      case _                          => MergeStrategy.first
    }

  case PathList("module-info.class") =>
    // Удаляем module-info (Java-модули конфликтуют) :contentReference[oaicite:1]{index=1}
    MergeStrategy.discard

  case PathList("google", "protobuf", _ @ _*) =>
    // Берём первый файл с .proto (protobuf-схемы) :contentReference[oaicite:2]{index=2}
    MergeStrategy.first

  case PathList("META-INF", "services", _ @ _*) =>
    // Конкатенируем SPI-конфигурации
    MergeStrategy.concat

  case PathList("META-INF", xs @ _*) if xs.last.endsWith(".prov") =>
    // Пример: отбрасываем провижен-файлы, если они мешают
    MergeStrategy.discard

  case PathList("META-INF", "versions", _ @ _*) =>
    // Удаляем module-info в META-INF/versions/11 :contentReference[oaicite:3]{index=3}
    MergeStrategy.discard

  case "reference.conf" | "application.conf" =>
    // Конкатенируем конфиги Typesafe
    MergeStrategy.concat

  case PathList(ps @ _*) if ps.last.endsWith(".html") =>
    // Берём первый HTML (документация)
    MergeStrategy.first


  case PathList("org","apache","commons","logging", _ @ _*) =>
    // Убираем дубли классов из commons-logging vs jcl-over-slf4j :contentReference[oaicite:0]{index=0}
    MergeStrategy.first

  case PathList("org","slf4j","jcl_over_slf4j", _ @ _*) =>
    // Аналогично, оставляем первый из jcl-over-slf4j
    MergeStrategy.first

  case PathList("META-INF", "services", xs @ _*) =>
    // Сливаем файлы SPI (ServiceLoader) :contentReference[oaicite:1]{index=1}
    MergeStrategy.concat

  case PathList("google","protobuf", _ @ _*) =>
    // Берём первую версию .proto из spark-core или protobuf-java :contentReference[oaicite:2]{index=2}
    MergeStrategy.first

  case PathList("META-INF", "versions", _ @ _*) =>
    // Убираем module-info внутри META-INF/versions/11 :contentReference[oaicite:3]{index=3}
    MergeStrategy.discard

  case PathList(ps @ _*) if ps.last == "arrow-git.properties" =>
    // Дублирование arrow-git.properties из разных arrow-jar'ов — удаляем :contentReference[oaicite:4]{index=4}
    MergeStrategy.discard

  case PathList(ps @ _*) if ps.last.endsWith(".class") && ps.contains("logging") =>
    // Любые оставшиеся дубли .class в папках logging — берём первый
    MergeStrategy.first

  case PathList("META-INF", xs @ _*) =>
    // Остальные META-INF.* — отбрасываем (manifest, index, etc.)
    MergeStrategy.discard

  case "reference.conf" | "application.conf" =>
    // Конкатенируем все конфиги Typesafe
    MergeStrategy.concat


  case PathList("META-INF", file) if file.endsWith(".SF")  => MergeStrategy.discard  // подписи :contentReference[oaicite:1]{index=1}
  case PathList("META-INF", file) if file.endsWith(".RSA") => MergeStrategy.discard  // подписи :contentReference[oaicite:2]{index=2}
  case PathList("META-INF", file) if file.endsWith(".DSA") => MergeStrategy.discard  // подписи :contentReference[oaicite:3]{index=3}

  case PathList("org","apache","commons","logging", _ @ _*) =>
    MergeStrategy.first                                                        // commons-logging vs jcl-over-slf4j :contentReference[oaicite:4]{index=4}

  case PathList("org","slf4j","jcl_over_slf4j", _ @ _*) =>
    MergeStrategy.first                                                        // jcl-over-slf4j :contentReference[oaicite:5]{index=5}

  case PathList("google","protobuf", _ @ _*) =>
    MergeStrategy.first                                                        // .proto из Spark & Protobuf :contentReference[oaicite:6]{index=6}

  case PathList(ps @ _*) if ps.last == "arrow-git.properties" =>
    MergeStrategy.discard                                                       // дубли arrow-git.properties :contentReference[oaicite:7]{index=7}

  case PathList("META-INF", "services", _ @ _*) =>
    MergeStrategy.concat                                                        // слияние SPI-файлов :contentReference[oaicite:8]{index=8}

  case PathList("META-INF", "versions", _ @ _*) =>
    MergeStrategy.discard                                                       // multi-release module-info :contentReference[oaicite:9]{index=9}

  case "reference.conf" | "application.conf" =>
    MergeStrategy.concat                                                        // Typesafe Config :contentReference[oaicite:10]{index=10}

  case PathList("META-INF", _ @ _*) =>
    MergeStrategy.discard

  case x =>
    // Для всего прочего — дефолтная стратегия
    val old = (assembly / assemblyMergeStrategy).value
    old(x)
}


