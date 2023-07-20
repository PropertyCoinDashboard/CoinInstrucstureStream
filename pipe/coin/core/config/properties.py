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

BTC_TOPIC_NAME: str = parser.get("TOPICNAME", "BTC_TOPIC_NAME")
ETH_TOPIC_NAME: str = parser.get("TOPICNAME", "ETHER_TOPIC_NAME")
OTHER_TOPIC_NAME: str = parser.get("TOPICNAME", "OTHER_TOPIC_NAME")

BTC_AVERAGE_TOPIC_NAME: str = parser.get("AVERAGETOPICNAME", "BTC_AVERAGE_TOPIC_NAME")
ETH_AVERAGE_TOPIC_NAME: str = parser.get("AVERAGETOPICNAME", "ETHER_AVERAGE_TOPIC_NAME")


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
                "max_price",
                "min_price",
                "prev_closing_price",
                "units_traded_24H",
            ),
        },
        "korbit": {
            "api": kwargs["korbit"],
            "timestamp": "timestamp",
            "parameter": ("open", "high", "low", "last", "volume"),
        },
    }
    return market
