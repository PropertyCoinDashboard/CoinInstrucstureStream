from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import to_json, from_json, expr, col
from schema.data_constructure import average_schema, market_schema


# setting initalization
spark = (
    SparkSession.builder.appName("CoinMarketPresentPriceAverage")
    .master("local[*]")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0")
    .config("spark.streaming.stopGracefullyOnShutdown", "true")
    .getOrCreate()
)

streaming_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafk1:9092, kafka2:9093, kafka3:9094")
    .option("subscribe", "tradebitcointotal")
    .option("startOffsets", "earliest")
    .load()
)

# update streaming_df after transformations
streaming_df = streaming_df.selectExpr("CAST(value AS STRING)").select(
    from_json("value", schema=market_schema).alias("crypto")
)
streaming_df.printSchema()
streaming_df.createOrReplaceTempView("injectioncoin")

d = spark.sql(
    "SELECT crypto.upbit.data, crypto.bithumb.data, crypto.korbit.data FROM injectioncoin"
)
query = (
    d.writeStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafk1:9092, kafka2:9093, kafka3:9094")
    .option("topic", "TestAverage")
    .option(
        "value.serializer",
        "org.apache.kafka.common.serialization.ByteArraySerializer",
    )
    .option("checkpointLocation", f".checkpointLocationTTTT")
    .start()
)
query.awaitTermination()
