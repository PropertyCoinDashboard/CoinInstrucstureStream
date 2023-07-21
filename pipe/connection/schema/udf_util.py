"""
pyspark udf 
"""

import numpy as np
from dataclasses import dataclass, asdict
from typing import Any
import datetime


def get_utc_time() -> int:
    utc_now = datetime.datetime.utcnow()
    return int(utc_now.timestamp())


# 데이터 규격
@dataclass
class CoinPrice:
    opening_price: float
    closing_price: float
    max_price: float
    min_price: float
    prev_closing_price: float
    acc_trade_volume_24h: float


@dataclass
class StreamingData:
    name: str
    time: int
    data: CoinPrice


def streaming_preprocessing(name: str, *data: tuple) -> dict[str, Any]:
    """average coin price normalization in spark python udf

    Args:
        - name (str): coin_symbol \n
    Returns:
        ex)
        >>> "average_price": {
                "name": "ETH",
                "timestamp": 1689633864.89345,
                "data": {
                    "opening_price": 2455000.0,
                    "closing_price": 2439000.0,
                    "trade_price": 38100000.0,
                    "max_price": 2462000.0,
                    "min_price": 2431000.0,
                    "prev_closing_price": 2455000.0,
                    "acc_trade_volume_24h": 11447.928,
                }
            }

    """
    roww: list[tuple] = [d for d in data]
    value = list(zip(*roww))
    average: list = np.mean(value, axis=1).tolist()

    data_dict = CoinPrice(
        opening_price=float(average[0]),
        closing_price=float(average[1]),
        max_price=float(average[2]),
        min_price=float(average[3]),
        prev_closing_price=float(average[4]),
        acc_trade_volume_24h=float(average[5]),
    )

    streaming_data = StreamingData(name=name, time=get_utc_time(), data=data_dict)
    return asdict(streaming_data)
