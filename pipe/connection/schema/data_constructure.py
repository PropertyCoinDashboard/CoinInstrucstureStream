"""
pyspark data schema
{
    "upbit": {
        "name": "upbit-ETH",
        "timestamp": 1689633864.89345,
        "data": {
            "opening_price": 2455000.0,
            "closing_price": 2439000.0,
            "max_price": 2462000.0,
            "min_price": 2431000.0,
            "prev_closing_price": 2455000.0,
            "acc_trade_volume_24h": 11447.92825886,
        }
    }
}
"""
from pyspark.sql.types import (
    StructField,
    StructType,
    StringType,
    IntegerType,
    FloatType,
)


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
                                StructField("opening_price", FloatType()),
                                StructField("closing_price", FloatType()),
                                StructField("max_price", FloatType()),
                                StructField("min_price", FloatType()),
                                StructField("prev_closing_price", FloatType()),
                                StructField("acc_trade_volume_24h", FloatType()),
                            ]
                        ),
                    ),
                ]
            ),
        )
    ]
)
