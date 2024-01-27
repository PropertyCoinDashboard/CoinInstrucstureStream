"""
기능 분할 완료 
1. WebsocketConnectionManager
    - 웹소켓 승인 및 전송 로직
2. MessageDataPreprocessing
    - 메시지 스키마 통일화 전처리 로직 
3. KafkaMessageSender
    - 카프카 전송 로직 
    - 전송 실패 했을 시 우회 로직 완료 
"""

from __future__ import annotations
from typing import Any


from abc import ABC, abstractmethod


class WebsocketConnectionAbstract(ABC):
    """
    1. WebsocketConnectionManager
        - 웹소켓 승인 및 전송 로직
    """

    @abstractmethod
    def __init__(self, message_logger: MessageDataPreprocessingAbstract) -> None:
        """
        전처리 할 데이터 전송

        Args:
            message_logger (MessageDataPreprocessing):
                -> 전처리 클래스
        """
        pass

    @abstractmethod
    async def send_data(self, websocket: Any, subscribe_fmt: list[dict]) -> None:
        """웹소켓 승인 함수

        Args:
            websocket (Any):
                -> 업비트, 빗썸, 코빗
            subscribe_fmt (list[dict]):
                -> 각 웹소켓당 승인 list[dictionary] 전송 로직
        """
        pass

    @abstractmethod
    async def handle_connection(self, websocket: Any, uri: str) -> None:
        """웹 소켓 커넥션 확인 함수

        Args:
            websocket (Any):
                -> 업비트, 빗썸, 코빗
            uri (str):
                ->각 uri들
        """
        pass

    @abstractmethod
    async def handle_message(self, websocket: Any, uri: str, symbol: str) -> None:
        """승인된 소켓 메시지를 전처리 클래스에전송할 로직

        Args:
            websocket (Any):
                -> 업비트, 빗썸, 코빗
            uri (str):
                -> 각 uri
            symbol (emf):
                -> 코인 심볼
        """
        pass

    @abstractmethod
    async def websocket_to_json(
        self, uri: str, subscribe_fmt: list[dict], symbol: str
    ) -> None:
        """말단 소켓 시작 지점

        Args:
            uri (str)
                -> 소켓을 지원하는 uri
            subscribe_fmt (list[dict])
                -> 웹소켓 승인 스키마
            symbol (str):
                -> 코인 심볼
        """
        pass


class MessageDataPreprocessingAbstract(ABC):
    """
    2. MessageDataPreprocessing
        -> 메시지 스키마 통일화 전처리 로직
    """

    @abstractmethod
    def __init__(self) -> None:
        """각 설정값들

        Args:
            kafka_sender (KafkaMessageSender)
                -> 카프카 producre 클래스 연결

            message_by_data (defaultdict(list))
                -> 카프카에 담아서 보낼 dictionary

            market
                -> 설정값(from coin.core.settings.properties import market_setting)

            register_message
                -> 빗썸과 코빗은 소켓에서 연결 확인 메시지가 출력되고 그다음 데이터가 출력되기 때문에 데이터 오염이 발생할 수 있어 필터링
        """
        pass

    @abstractmethod
    async def put_message_to_logging(self, message: Any, uri: str, symbol: str) -> None:
        """
        필터링 후 스키마 통일화 카프카로 보내는 logging

        Args:
            message (Any):
                -> 데이터들
            uri (str):
                -> 각각 uri
            symbol (str):
                -> 코인 심볼
        """
        pass

    @abstractmethod
    async def process_message(
        self, market: str, message: dict, symbol: str
    ) -> dict[str, Any]:
        """market_socket.json 에서 설정된 값 추출

        Args:
            market (str):
                -> 거래소 이름
            message (dict):
                -> 데이터
            symbol (str):
                -> 코인심볼

        Returns:
            dict[str, Any]:
                >>> 2023-08-03 20:07:10,865 - total - INFO - {
                    'market': 'upbit-BTC',
                    'time': 1691060828128,
                    'coin_symbol': 'BTC',
                    'data': {
                           'opening_price': '38358000.000',
                           'trade_price': '38477000.000',
                           'max_price': '38510000.000',
                           'min_price': '38215000.000',
                           'prev_closing_price': '38358000.000',
                           'acc_trade_volume_24h': '2297.878'
                        }
                    }

        """
        pass

    @abstractmethod
    async def process_exchange(self, market: str, message: dict) -> dict:
        """
        message 필터링

        Args:
            market (str):
                -> 거래소
            message (dict):
                -> 데이터

        Returns:
            dict: 각 거래소당 dictionary가 달라 저렇게 항목으로 접근
        """
        pass

    @abstractmethod
    async def unify_schema(
        self,
        market: str,
        symbol: str,
        time: str,
        schema_key: dict,
        parameter: list,
    ) -> dict[str, Any]:
        """스키마 전처리

        Args:
            market (str):
                -> 거래소 이름
            symbol (str):
                -> 코인심볼
            time (str):
                -> 시간
            schema_key (dict):
                -> 전처리할 스키마 대상
            parameter (list):
                -> JSON으로 부터 가지고온 스키마

        Returns:
            dict[str, Any]:
                >>> {
                        'market': 'upbit-BTC',
                        'time': 1691060828128,
                        'coin_symbol': 'BTC',
                        'data': {
                            'opening_price': '38358000.000',
                            'trade_price': '38477000.000',
                            'max_price': '38510000.000',
                            'min_price': '38215000.000',
                            'prev_closing_price': '38358000.000', ∂
                            'acc_trade_volume_24h': '2297.878'
                        }
                    }

        """
        pass
