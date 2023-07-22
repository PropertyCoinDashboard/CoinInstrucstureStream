"""
setting 
"""
import configparser
from typing import Any


parser = configparser.ConfigParser()
parser.read("coin/urls.conf")

UPBIT_URL: str = parser.get("APIURL", "UPBIT")
BITHUMB_URL: str = parser.get("APIURL", "BITHUMB")
KORBIT_URL: str = parser.get("APIURL", "KORBIT")
COINONE: str = parser.get("APIURL", "COINONE")


def market_setting(**kwargs) -> dict[str, dict[str, Any]]:
    """_summary_

    Returns:
        dict[str, dict[str, Any]]: market env setting 관리 포인트
    """
    market = {
        "upbit": {
            "api": kwargs["upbit"],
            "timestamp": "trade_timestamp",
            "parameter": (
                "opening_price",
                "trade_price",
                "high_price",
                "low_price",
                "prev_closing_price",
                "acc_trade_volume_24h",
            ),
        },
        "bithumb": {
            "api": kwargs["bithumb"],
            "timestamp": "date",
            "parameter": (
                "opening_price",
                "closing_price",
                "max_price",
                "min_price",
                "prev_closing_price",
                "units_traded_24H",
            ),
        },
        "coinone": {
            "api": kwargs["coinone"],
            "timestamp": "timestamp",
            "parameter": (
                "first",
                "last",
                "high",
                "low",
                "yesterday_last",
                "target_volume",
            ),
        },
        "korbit": {
            "api": kwargs["korbit"],
            "timestamp": "timestamp",
            "parameter": ("open", "last", "high", "low", "last", "volume"),
        },
    }

    return market
