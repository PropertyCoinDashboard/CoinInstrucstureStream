import json
from typing import Any
from pathlib import Path


from coin.core.ubkc_market import (
    UpbitRestAndSocket,
    BithumbRestAndSocket,
    KorbitRestAndSocket,
    CoinoneRestAndSocket,
)
from coin.core.util._typing import (
    ExchangeRestDataTypeHints,
    ExchangeSocketDataTypeHints,
)

path = Path(__file__).parent.parent


class __MarketAPIFactory:
    """Factory for market APIs."""

    _create: dict[str, dict[str, Any]] = {
        "upbit": UpbitRestAndSocket,
        "bithumb": BithumbRestAndSocket,
        "korbit": KorbitRestAndSocket,
        "coinone": CoinoneRestAndSocket,
    }

    @classmethod
    def market_load(cls, conn_type: str, *args, **kwargs):
        """
        거래소 API의 인스턴스를 생성합니다.
        """
        if conn_type not in cls._create:
            raise ValueError(f"잘못된 연결 유형: {conn_type}")

        creator = cls._create[conn_type]
        return creator(*args, **kwargs)


def load_json(
    conn_type: str,
) -> ExchangeSocketDataTypeHints | ExchangeRestDataTypeHints:
    """
    Open the file and load market information.

    ExchangeRestDataTypeHints(Type): dict[str, ExchangeRestConfig]
    - from coin.core.util._typing import ExchangeRestDataTypeHints

    ExchangeSocketDataTypeHints(Type): dict[str, ExchangeSocketConfig]
    - from coin.core.util._typing import ExchangeSocketDataTypeHints


    """
    with open(
        file=f"{path}/config/_market_{conn_type}.json", mode="r", encoding="utf-8"
    ) as file:
        market_info = json.load(file)

    # ExchangeSocketDataTypeHints | ExchangeRestDataTypeHints
    # JSON에 저장되어 있는 값 + API 클래스 주소
    market_info = {
        market: {**info, "api": __MarketAPIFactory.market_load(market)}
        for market, info in market_info.items()
    }
    return market_info
