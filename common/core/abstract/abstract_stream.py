from __future__ import annotations
from typing import Any


from abc import ABC, abstractmethod
from common.core.types import SubScribeFormat


class WebsocketConnectionAbstract(ABC):
    """
    1. WebsocketConnectionManager
        - 웹소켓 승인 및 전송 로직
    """

    @abstractmethod
    async def socket_param_send(
        self, websocket: Any, subscribe_fmt: SubScribeFormat
    ) -> None:
        """웹소켓 승인 함수
        Args:
            websocket (Any):
                -> 업비트, 빗썸, 코인원
            subscribe_fmt (SubScribeFormat):
                -> 각 웹소켓당 승인 list[dictionary] 전송 로직
        """
        raise NotImplementedError()

    @abstractmethod
    async def handle_connection(self, websocket: Any, uri: str) -> None:
        """웹 소켓 커넥션 확인 함수
        Args:
            websocket (Any):
                -> 업비트, 빗썸, 코인원
            uri (str):
                ->각 uri들
        """
        raise NotImplementedError()

    @abstractmethod
    async def handle_message(self, websocket: Any, uri: str, symbol: str) -> None:
        """승인된 소켓 메시지를 전처리 클래스에전송할 로직
        Args:
            websocket (Any):
                -> 업비트, 빗썸, 코인원
            uri (str):
                -> 각 uri
            symbol (emf):
                -> 코인 심볼
        """
        raise NotImplementedError()

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
        raise NotImplementedError()


class MessageDataPreprocessingAbstract(ABC):
    """
    2. MessageDataPreprocessing
        -> 메시지 스키마 통일화 전처리 로직
    """

    @abstractmethod
    async def put_message_to_logging(self, message: Any, uri: str, symbol: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def process_message(
        self, market: str, message: dict, symbol: str
    ) -> dict[str, Any]:
        raise NotImplementedError()
