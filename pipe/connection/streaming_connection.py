from typing import *
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql.functions import from_json, col, udf, to_json, struct
from schema.data_constructure import market_schema, average_schema, final_schema
from schema.udf_util import streaming_preprocessing

spark = (
    SparkSession.builder.appName("myAppName")
    .master("local[*]")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .getOrCreate()
)


stream_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafka1:19092,kafka2:29092,kafka3:39092")
    .option("subscribe", "tradeethertotal")
    .option("startingOffsets", "earliest")
    .load()
)

average_udf = udf(streaming_preprocessing, average_schema)
data_df = (
    stream_df.selectExpr("CAST(value AS STRING)")
    .select(from_json("value", schema=final_schema).alias("crypto"))
    .selectExpr(
        "split(crypto.upbit.market, '-')[1] as name",
        "crypto.upbit.data as upbit_price",
        "crypto.bithumb.data as bithumb_price",
        "crypto.korbit.data as korbit_price",
    )
    .withColumn(
        "average_price",
        average_udf(
            col("name"),
            col("upbit_price"),
            col("bithumb_price"),
            col("korbit_price"),
        ).alias("average_price"),
    )
    .select(to_json(col("average_price")).alias("value"))
)

query = (
    data_df.writeStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafka1:19092,kafka2:29092,kafka3:39092")
    .option("topic", "TestAverage")
    .option("checkpointLocation", f".checkpoint_tt")
    .option(
        "value.serializer",
        "org.apache.kafka.common.serialization.ByteArraySerializer",
    )
    .start()
)

query.awaitTermination()
