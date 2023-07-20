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
{
    "upbit": {
        "market": "upbit-BTC",
        "time": 1689839839781,
        "coin_symbol": "BTC",
        "parameter": {
            "opening_price": 38322000.0,
            "high_price": 38840000.0,
            "low_price": 38316000.0,
            "prev_closing_price": 38323000.0,
            "acc_trade_volume_24h": 2247.1176924,
        },
    },
    "bithumb": {
        "market": "bithumb-BTC",
        "time": 1689839844110,
        "coin_symbol": "BTC",
        "parameter": {
            "opening_price": "38292000",
            "max_price": "38779000",
            "min_price": "38232000",
            "prev_closing_price": "38292000",
            "units_traded_24H": "1572.57815975",
        },
    },
    "korbit": {
        "market": "korbit-BTC",
        "time": 1689839720270,
        "coin_symbol": "BTC",
        "parameter": {
            "open": "38459000",
            "high": "38811000",
            "low": "38265000",
            "last": "38810000",
            "volume": "32.59161199",
        },
    },
}
from pyspark.sql.types import (
    StructField,
    StructType,
    StringType,
    IntegerType,
    DoubleType,
)

# 평균값
average_schema = StructType(
    [
        StructField(
            "average",
            StructType(
                [
                    StructField("name", StringType()),
                    StructField("time", IntegerType()),
                    StructField(
                        "data",
                        StructType(
                            [
                                StructField("opening_price", DoubleType()),
                                StructField("max_price", DoubleType()),
                                StructField("min_price", DoubleType()),
                                StructField("prev_closing_price", DoubleType()),
                                StructField("acc_trade_volume_24h", DoubleType()),
                            ]
                        ),
                    ),
                ]
            ),
        )
    ]
)


market_schema = StructType(
    [
        StructField(
            "upbit",
            StructType(
                [
                    StructField("name", StringType()),
                    StructField("time", IntegerType()),
                    StructField(
                        "data",
                        StructType(
                            [
                                StructField("opening_price", DoubleType()),
                                StructField("high_price", DoubleType()),
                                StructField("low_price", DoubleType()),
                                StructField("prev_closing_price", DoubleType()),
                                StructField("acc_trade_volume_24h", DoubleType()),
                            ]
                        ),
                    ),
                ]
            ),
        ),
        StructField(
            "bithumb",
            StructType(
                [
                    StructField("name", StringType()),
                    StructField("time", IntegerType()),
                    StructField(
                        "data",
                        StructType(
                            [
                                StructField("opening_price", DoubleType()),
                                StructField("max_price", DoubleType()),
                                StructField("min_price", DoubleType()),
                                StructField("prev_closing_price", DoubleType()),
                                StructField("units_traded_24H", DoubleType()),
                            ]
                        ),
                    ),
                ]
            ),
        ),
        StructField(
            "korbit",
            StructType(
                [
                    StructField("name", StringType()),
                    StructField("time", IntegerType()),
                    StructField(
                        "data",
                        StructType(
                            [
                                StructField("open", DoubleType()),
                                StructField("high", DoubleType()),
                                StructField("low", DoubleType()),
                                StructField("last", DoubleType()),
                                StructField("volume", DoubleType()),
                            ]
                        ),
                    ),
                ]
            ),
        ),
    ]
)
