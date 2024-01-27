import json
from typing import Any
from pathlib import Path

from coin.restpull.coin_apis_rest import (
    UpbitRest,
    BithumbRest,
    CoinoneRest,
    KorbitRest,
)

from coin.streaming.coin_apis_socket import (
    UpbitSocket,
    BithumbSocket,
    KorbitSocket,
)

path = Path(__file__).parent.parent


class __MarketAPIFactory:
    """Factory for market APIs."""

    _create: dict[str, dict[str, Any]] = {
        "rest": {
            "upbit": UpbitRest,
            "bithumb": BithumbRest,
            "coinone": CoinoneRest,
            "korbit": KorbitRest,
        },
        "socket": {
            "upbit": UpbitSocket,
            "bithumb": BithumbSocket,
            "korbit": KorbitSocket,
        },
    }

    @classmethod
    def market_load(cls, conn_type: str, market: str, *args, **kwargs):
        """
        거래소 API의 인스턴스를 생성합니다.
        """
        if conn_type not in cls._create:
            raise ValueError(f"잘못된 연결 유형: {conn_type}")

        if market not in cls._create[conn_type]:
            raise ValueError(f"잘못된 거래소: {market}")

        creator = cls._create[conn_type][market]
        return creator(*args, **kwargs)


def load_json(conn_type: str):
    """
    Open the file and load market information.

    ExchangeDataTypeHints(Type): dict[str, ExchangeConfig]
    - from coin.core.util._typing import ExchangeDataTypeHints
    """
    with open(
        file=f"{path}/config/_market_{conn_type}.json", mode="r", encoding="utf-8"
    ) as file:
        market_info = json.load(file)

    market_info = {
        market: {**info, "api": __MarketAPIFactory.market_load(conn_type, market)}
        for market, info in market_info.items()
    }
    return market_info
