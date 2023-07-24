"""
setting 
"""
import json
from typing import Any
from pathlib import Path

from coin.core.market.coin_apis import (
    UpbitCoinPullRequest,
    BithumbCoinPullRequest,
    CoinoneCoinPullRequest,
    KorbitCoinPullRequest,
)

path = Path(__file__).parent.parent


class MarketAPIFactory:
    """factory market API

    Raises:
        ValueError: 거래소가 없을떄

    Returns:
        _type_: 각 거래소 클래스 주소
    """

    _create: dict[str, Any] = {
        "upbit": UpbitCoinPullRequest,
        "bithumb": BithumbCoinPullRequest,
        "coinone": CoinoneCoinPullRequest,
        "korbit": KorbitCoinPullRequest,
    }

    @classmethod
    def market_load(cls, name, *args, **kwargs):
        """
        Create an instance of an exchange API.
        """

        if name not in cls._create:
            raise ValueError(f"Invalid name: {name}")

        creator = cls._create[name]
        return creator(*args, **kwargs)


def market_setting() -> dict[str, dict[str, Any]]:
    """_summary_

    Returns:
        dict[str, dict[str, Any]]: market env setting 관리 포인트
    """
    with open(file=f"{path}/config/market.json", mode="r", encoding="utf-8") as file:
        market_info = json.load(file)

    market_info = {
        market: {**info, "api": MarketAPIFactory.market_load(market)}
        for market, info in market_info.items()
    }

    return market_info
