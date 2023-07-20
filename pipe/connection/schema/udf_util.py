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


@dataclass
class CoinPrice:
    opening_price: float
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
    roww: list[tuple] = [d for d in data]
    value = list(zip(*roww))
    average: list = np.mean(value, axis=1).tolist()

    data_dict = CoinPrice(
        opening_price=float(average[0]),
        max_price=float(average[1]),
        min_price=float(average[2]),
        prev_closing_price=float(average[3]),
        acc_trade_volume_24h=float(average[4]),
    )

    streaming_data = StreamingData(name=name, time=get_utc_time(), data=data_dict)
    return asdict(streaming_data)
