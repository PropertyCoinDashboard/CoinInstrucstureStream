"""
pyspark data schema
{
    "upbit": {
        "name": "upbit-ETH",
        "timestamp": 1689633864.89345,
        "data": {
            "opening_price": 2455000.0,
            "max_price": 2462000.0,
            "min_price": 2431000.0,
            "prev_closing_price": 2455000.0,
            "acc_trade_volume_24h": 11447.92825886,
        }
    },
    .....
}

"""

from pyspark.sql.types import (
    StructField,
    StructType,
    StringType,
    DoubleType,
    LongType,
)


data_schema = StructType(
    [
        StructField("opening_price", DoubleType(), True),
        StructField("max_price", DoubleType(), True),
        StructField("min_price", DoubleType(), True),
        StructField("prev_closing_price", DoubleType(), True),
        StructField("acc_trade_volume_24h", DoubleType(), True),
    ]
)

market_schema = StructType(
    [
        StructField("market", StringType(), True),
        StructField("time", LongType(), True),
        StructField("data", data_schema),
    ]
)

final_schema = StructType(
    [
        StructField("upbit", market_schema),
        StructField("bithumb", market_schema),
        StructField("korbit", market_schema),
    ]
)

# 평균값
average_schema = StructType(
    StructType(
        [
            StructField("name", StringType()),
            StructField("time", LongType()),
            StructField("data", data_schema),
        ]
    ),
)
