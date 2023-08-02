"""
Spark streaming coin average price 
"""

from typing import *
from pyspark.sql import SparkSession
from pyspark.sql.types import ArrayType

from pyspark.sql.functions import from_json, col, explode
from schema.data_constructure import market_schema
from properties import (
    BITHUMB_BTC_REAL_TOPIC_NAME,
    UPBIT_BTC_REAL_TOPIC_NAME,
    KORBIT_BTC_REAL_TOPIC_NAME,
)

# 환경 설정
spark = (
    SparkSession.builder.appName("myAppName")
    .master("local[*]")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .config("spark.streaming.stopGracefullyOnShutdown", "true")
    .getOrCreate()
)

stream_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafka1:19092,kafka2:29092,kafka3:39092")
    .option(
        "subscribe",
        f"{UPBIT_BTC_REAL_TOPIC_NAME},{KORBIT_BTC_REAL_TOPIC_NAME},{BITHUMB_BTC_REAL_TOPIC_NAME}",
    )
    .option("startingOffsets", "earliest")
    .load()
)


# JSON 배열을 문자열로 변환
json_array_str = stream_df.selectExpr("CAST(value AS STRING)")

# JSON 배열을 개별 로우로 변환
json_objects_df = json_array_str.select(
    explode(from_json(col("value"), ArrayType(market_schema))).alias("parsed_value")
)
flatten_data_df = json_objects_df.select(
    col("parsed_value.market").alias("market"),
    col("parsed_value.time").alias("time"),
    col("parsed_value.coin_symbol").alias("symbol"),
    col("parsed_value.data.*"),
)
flatten_data_df.printSchema()
flatten_data_df.createOrReplaceTempView("coinprice")


qs = """
SELECT
    symbol as coin,
    AVG(CAST(opening_price AS DOUBLE)) as opening_price,
    AVG(CAST(trade_price AS DOUBLE)) as trade_price,
    AVG(CAST(max_price AS DOUBLE)) as max_price,
    AVG(CAST(min_price AS DOUBLE)) as min_price,
    AVG(CAST(prev_closing_price AS DOUBLE)) as prev_closing_price,
    AVG(CAST(acc_trade_volume_24h AS DOUBLE)) as acc_trade_volume_24h
FROM
    coinprice
GROUP BY
    symbol
"""
average_df = spark.sql(qs)

# 결과를 콘솔에 출력
query = average_df.writeStream.outputMode("complete").format("console").start()

query.awaitTermination()
