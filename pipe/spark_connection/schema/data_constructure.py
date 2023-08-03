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
from pydantic import BaseModel
from pyspark.sql.types import (
    StructField,
    StructType,
    StringType,
    LongType,
)


data_schema = StructType(
    [
        StructField("opening_price", StringType(), True),
        StructField("trade_price", StringType(), True),
        StructField("max_price", StringType(), True),
        StructField("min_price", StringType(), True),
        StructField("prev_closing_price", StringType(), True),
        StructField("acc_trade_volume_24h", StringType(), True),
    ]
)

market_schema = StructType(
    [
        StructField("market", StringType(), True),
        StructField("time", LongType(), True),
        StructField("coin_symbol", StringType(), True),
        StructField("data", data_schema),
    ]
)

final_schema = StructType(
    [
        StructField("upbit", market_schema),
        StructField("bithumb", market_schema),
        StructField("coinone", market_schema),
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


class CoinPrice(BaseModel):
    opening_price: float
    closing_price: float
    max_price: float
    min_price: float
    prev_closing_price: float
    acc_trade_volume_24h: float


class StreamingData(BaseModel):
    name: str
    time: int
    data: CoinPrice
