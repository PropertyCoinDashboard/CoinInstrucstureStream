"""
Spark streaming coin average price 
"""

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql.functions import from_json, col, udf, to_json, struct
from spark_connection.schema.data_constructure import average_schema, final_schema
from spark_connection.schema.udf_util import streaming_preprocessing


# 환경 설정
spark = (
    SparkSession.builder.appName("myAppName")
    .master("local[*]")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .config("spark.streaming.stopGracefullyOnShutdown", "true")
    .getOrCreate()
)


def stream_injection(topic: str) -> "DataFrame":
    """spark streaming multithreading

    Args:
        - topic (str): topic \n
    Returns:
        - DataFrame: query
    """

    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "kafka1:19092,kafka2:29092,kafka3:39092")
        .option("subscribe", "".join(topic))
        .option("startingOffsets", "earliest")
        .load()
    )


def preprocessing(topic: str):
    stream_df = stream_injection(topic=topic)
    average_udf = udf(streaming_preprocessing, average_schema)

    return (
        stream_df.selectExpr("CAST(value AS STRING)")
        .select(from_json("value", schema=final_schema).alias("crypto"))
        .selectExpr(
            "split(crypto.upbit.market, '-')[1] as name",
            "crypto.upbit.data as upbit_price",
            "crypto.bithumb.data as bithumb_price",
            "crypto.coinone.data as coinone_price",
            "crypto.korbit.data as korbit_price",
        )
        .withColumn(
            "average_price",
            average_udf(
                col("name"),
                col("upbit_price"),
                col("bithumb_price"),
                col("coinone_price"),
                col("korbit_price"),
            ).alias("average_price"),
        )
        .select(to_json(struct(col("average_price"))).alias("value"))
    )


def run_spark_streaming(name: str, topics: str, retrieve_topic: str) -> None:
    """KAFKA interaction TOPIC Sending data

    Args:
        name (str): coin_symbol
        topics (str): topic
        retrieve_topic (str): retrieve_topic
    """
    data_df = preprocessing(topic=topics)
    query = (
        data_df.writeStream.format("kafka")
        .option("kafka.bootstrap.servers", "kafka1:19092,kafka2:29092,kafka3:39092")
        .option("topic", retrieve_topic)
        .option("checkpointLocation", f".checkpoint_{name}")
        .option(
            "value.serializer",
            "org.apache.kafka.common.serialization.ByteArraySerializer",
        )
        .start()
    )

    query.awaitTermination()
