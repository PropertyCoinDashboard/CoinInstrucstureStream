"""
Spark streaming coin average price 
"""

from typing import *
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    LongType,
    ArrayType,
)
from pyspark.sql.functions import from_json, col, mean, avg, explode
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
    .option("subscribe", UPBIT_BTC_REAL_TOPIC_NAME)
    .option("startingOffsets", "earliest")
    .load()
)


# 스키마 정의
data_schema = StructType(
    [
        StructField("opening_price", DoubleType()),
        StructField("trade_price", DoubleType()),
        StructField("high_price", DoubleType()),
        StructField("low_price", DoubleType()),
        StructField("prev_closing_price", DoubleType()),
        StructField("acc_trade_volume_24h", DoubleType()),
    ]
)

schema = StructType(
    [
        StructField("market", StringType()),
        StructField("time", LongType()),
        StructField("data", data_schema),
    ]
)
# JSON 배열을 문자열로 변환
json_array_str = stream_df.selectExpr("CAST(value AS STRING)")

# JSON 배열을 개별 로우로 변환
json_objects_df = json_array_str.select(
    explode(from_json(col("value"), ArrayType(schema))).alias("parsed_value")
)

data_df = json_objects_df.select("parsed_value.data.*")

# 모든 필드에 대한 평균 계산
average_df = data_df.agg(
    avg("opening_price"),
    avg("trade_price"),
    avg("high_price"),
    avg("low_price"),
    avg("prev_closing_price"),
    avg("acc_trade_volume_24h"),
)


# 결과를 콘솔에 출력
query = average_df.writeStream.outputMode("complete").format("console").start()

query.awaitTermination()
