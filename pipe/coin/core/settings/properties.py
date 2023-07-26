"""
setting 
"""
import json
from typing import Any
from pathlib import Path

from coin.core.market.coin_apis import (
    UpbitSocketAndPullRequest,
    BithumbSocketAndPullRequest,
    CoinoneSocketAndPullRequest,
    KorbitSocketAndPullRequest,
)

path = Path(__file__).parent.parent


class __MarketAPIFactory:
    """factory market API

    Raises:
        ValueError: 거래소가 없을떄

    Returns:
        _type_: 각 거래소 클래스 주소
    """

    _create: dict[str, Any] = {
        "upbit": UpbitSocketAndPullRequest,
        "bithumb": BithumbSocketAndPullRequest,
        "coinone": CoinoneSocketAndPullRequest,
        "korbit": KorbitSocketAndPullRequest,
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


def load_json(conn_type: str):
    """
    파일 열기..
    """
    with open(
        file=f"{path}/config/market_{conn_type}.json", mode="r", encoding="utf-8"
    ) as file:
        market_info = json.load(file)

    market_info = {
        market: {**info, "api": __MarketAPIFactory.market_load(market)}
        for market, info in market_info.items()
    }

    return market_info


def market_setting(conn_type: str) -> Any:
    """_summary_
    Args:
        - conn_ type (str)
            - rest
            - socket

    Returns:
        - rest : dict[str, dict[str, Any]]
        - socket : Any"""
    match conn_type:
        case "rest":
            return load_json("rest")
        case "socket":
            return load_json("socket")
        case _:
            raise ValueError("해당 포맷은 존재하지 않습니다")
