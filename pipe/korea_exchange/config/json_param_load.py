import json
from pathlib import Path
from common.core.types import KoreaMarketsLoadJson
from common.core.abstract import (
    AbstractExchangeRestClient,
    AbstractExchangeSocketClient,
)
from korea_exchange.driver.rest_korea_exchange import (
    UpbitRest,
    BithumbRest,
    CoinoneRest,
    KorbitRest,
)
from korea_exchange.driver.socket_korea_exchange import (
    UpbitSocket,
    BithumbSocket,
    CoinoneSocket,
)


path = Path(__file__).parent.parent

Market = UpbitRest | BithumbRest | KorbitRest | CoinoneRest
RestSocket = AbstractExchangeRestClient | AbstractExchangeSocketClient


class __MarketAPIFactory:
    """Factory for market APIs."""

    _create: dict[str, dict[str, RestSocket]] = {
        "rest": {
            "upbit": UpbitRest,
            "bithumb": BithumbRest,
            "korbit": KorbitRest,
            "coinone": CoinoneRest,
        },
        "socket": {
            "upbit": UpbitSocket,
            "bithumb": BithumbSocket,
            "coinone": CoinoneSocket,
        },
    }

    @classmethod
    def market_load(cls, conn_type: str, market: str, *args, **kwargs) -> Market:
        """
        거래소 API의 인스턴스를 생성합니다.
        """
        if conn_type not in cls._create:
            raise ValueError(f"잘못된 연결 유형: {conn_type}")

        creator = cls._create[conn_type][market]
        return creator(*args, **kwargs)


def load_json(conn_type: str) -> dict[str, str | Market]:
    """
    JSON 파일 로드 (socket 또는 rest)
        - 어떤 가격대를 가지고 올지 파라미터 정의되어 있음
    """
    with open(
        file=f"{path}/config/_market_{conn_type}.json", mode="r", encoding="utf-8"
    ) as file:
        market_info: KoreaMarketsLoadJson = json.load(file)

    # JSON에 저장되어 있는 값 + API 클래스 주소
    korea_markets: dict[str, str | Market] = {
        market: {
            **info,
            "api": __MarketAPIFactory.market_load(conn_type=conn_type, market=market),
        }
        for market, info in market_info.items()
    }
    return korea_markets
