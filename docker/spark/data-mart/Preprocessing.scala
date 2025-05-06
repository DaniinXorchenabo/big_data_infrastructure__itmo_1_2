package com.example.datamart.transform

import org.apache.spark.ml.feature.{StandardScaler, VectorAssembler}
import org.apache.spark.sql.{DataFrame, functions => F}

object Preprocessing {
  def transform(df: DataFrame): DataFrame = {
    val selected = df.select("ingredients_n","ingredients_sweeteners_n","scans_n","additives_n")
      .na.drop()

    val assembler = new VectorAssembler()
      .setInputCols(Array("ingredients_n","ingredients_sweeteners_n","scans_n","additives_n"))
      .setOutputCol("features_assembled")

    val assembled = assembler.transform(selected)

    val scaler = new StandardScaler()
      .setInputCol("features_assembled")
      .setOutputCol("features")
      .fit(assembled)

    scaler.transform(assembled).select("features")            # :contentReference[oaicite:11]{index=11}
  }
}
