"""
기능 분할 완료 
1. WebsocketConnectionManager
    - 웹소켓 승인 및 전송 로직
2. MessageDataPreprocessing
    - 메시지 스키마 통일화 전처리 로직 
3. KafkaMessageSender
    - 카프카 전송 로직 
    - 전송 실패 했을 시 우회 로직 완료 
4. CoinStreamFacade
    - 1~3번 통합 
"""
from __future__ import annotations
import json
import asyncio
from typing import Any
from collections import defaultdict

import websockets
from aiokafka.errors import KafkaConnectionError
from coin.core.settings.create_log import SocketLogCustomer
from coin.core.data_mq.data_interaction import produce_sending
from coin.core.market.data_format import CoinMarketData
from coin.core.market.coin_abstract_class import (
    WebsocketConnectionAbstract,
    MessageDataPreprocessingAbstract,
    KafkaMessageSenderAbstract,
)

MAXLISTSIZE = 10


def parse_uri(uri: str) -> str:
    """
    주어진 URI를 파싱해서 로그 이름을 반환하는 함수.

    Args:
        uri (str): 파싱할 URI.

    Returns:
        str: 로그 이름.
    """
    return uri.split("//")[1].split(".")[1]


class WebsocketConnectionManager(WebsocketConnectionAbstract):
    """
    1. WebsocketConnectionManager
        - 웹소켓 승인 및 전송 로직
    """

    def __init__(self, message_logger: MessageDataPreprocessing) -> None:
        """
        전처리 할 데이터 전송

        Args:
            message_logger (MessageDataPreprocessing):
                -> 전처리 클래스(로그 클래스 존재) [self.p = SocketLogCustomer()  # 로그 출력을 위한 객체]
        """
        self.message_logger = message_logger

    async def send_data(self, websocket: Any, subscribe_fmt: list[dict]) -> None:
        """웹소켓 승인 함수

        Args:
            websocket (Any):
                -> 업비트, 빗썸, 코빗
            subscribe_fmt (list[dict]):
                -> 각 웹소켓당 승인 list[dictionary] 전송 로직
        """
        subscribe_data: str = json.dumps(subscribe_fmt)
        await websocket.send(subscribe_data)
        await asyncio.sleep(1)

    async def handle_connection(self, websocket: Any, uri: str) -> None:
        """웹 소켓 커넥션 확인 함수

        Args:
            websocket (Any):
                -> 업비트, 빗썸, 코빗
            uri (str):
                ->각 uri들
        """
        message: str = await asyncio.wait_for(websocket.recv(), timeout=30.0)
        market: str = parse_uri(uri)
        data = json.loads(message)
        match data:
            case {"resmsg": "Connected Successfully"}:
                await self.message_logger.p.connection(
                    exchange_name=market, message=f"Connected to {uri}, {data}"
                )
            case {"event": "korbit:connected"}:
                await self.message_logger.p.connection(
                    exchange_name=market, message=f"Connected to {uri}, {data}"
                )
            case _:
                await self.message_logger.p.connection(
                    exchange_name=market, message=f"Connected to {uri}"
                )

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
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                await asyncio.sleep(1.0)
                await self.message_logger.put_message_to_logging(
                    message, uri, symbol=symbol
                )
            except asyncio.TimeoutError:
                await self.message_logger.p.error_log(
                    log_name=parse_uri(uri),
                    message=f"Timeout not connection while receiving from {uri}",
                )

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
        async with websockets.connect(uri) as websocket:
            try:
                await self.send_data(websocket, subscribe_fmt)
                await self.handle_connection(websocket, uri)
                await self.handle_message(websocket, uri, symbol=symbol)
            except asyncio.TimeoutError as error:
                self.message_logger.p.error_log(
                    error_type="total_not_connection",
                    message=f"Timeout while connecting to {uri}, Error: {error}",
                )


class MessageDataPreprocessing(MessageDataPreprocessingAbstract):
    """
    2. MessageDataPreprocessing
        -> 메시지 스키마 통일화 전처리 로직
    """

    def __init__(self, kafka_sender: KafkaMessageSender) -> None:
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
        from coin.core.settings.properties import market_setting

        self.p = SocketLogCustomer()
        self.kafka_sender = kafka_sender
        self.message_by_data = defaultdict(list)

        self.market = market_setting("socket")
        self.register_message = [
            "Filter Registered Successfully",
            "korbit:subscribe",
        ]

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
        market = parse_uri(uri)
        message = json.loads(message)

        # filter
        matches_all = any(ignore in message for ignore in self.register_message)

        if matches_all:
            await self.p.register_connection(message=message)
        else:
            try:
                market_schema: dict[str, Any] = await self.process_message(
                    market, message, symbol
                )
                self.message_by_data[market].append(market_schema)

                if len(self.message_by_data[market]) >= MAXLISTSIZE:
                    await self.kafka_sender.message_kafka_sending(
                        data=self.message_by_data[market],
                        market_name=market,
                        symbol=symbol,
                    )
                    self.message_by_data[market]: list[market] = []

                await self.p.data_log(
                    exchange_name=parse_uri(uri=uri), message=market_schema
                )
            except Exception as error:
                await self.p.error_log(
                    error_type="total_not_connection",
                    message=f"Price Socket Connection Error --> {error} url --> {market}",
                )

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
        processed_message: dict = await self.process_exchange(market, message)
        time: str = processed_message[self.market[market]["timestamp"]]
        parameter: list = list(self.market[market]["parameter"])
        schema_key: dict[str, Any] = {
            key: processed_message[key] for key in processed_message if key in parameter
        }

        return await self.unify_schema(market, symbol, time, schema_key, parameter)

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
        if market == "bithumb":
            return message["content"]
        elif market == "korbit":
            return message["data"]
        return message

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
                            'prev_closing_price': '38358000.000',
                            'acc_trade_volume_24h': '2297.878'
                        }
                    }

        """
        return CoinMarketData.from_api(
            market=f"{market}-{symbol.upper()}",
            time=time,
            coin_symbol=symbol.upper(),
            api=schema_key,
            data=parameter,
        ).model_dump(mode="json")


class KafkaMessageSender(KafkaMessageSenderAbstract):
    """
    3. KafkaMessageSender
        - 카프카 전송 로직
        - 전송 실패 했을 시 우회 로직 완료
    """

    def __init__(self) -> None:
        self.p = SocketLogCustomer()  # 로그 출력을 위한 객체
        self.except_list = defaultdict(list)

    async def message_kafka_sending(
        self, data: defaultdict[Any, list], market_name: str, symbol: str
    ) -> None:
        """카프카 전송 우회 로직 작성

        Args:
            data (defaultdict[Any, list]): 전처리된 데이터
            market_name (str): 마켓이름
            symbol (str): 코인심볼
        """
        try:
            await produce_sending(
                topic=f"{symbol.lower()}SocketDataIn{market_name.replace(market_name[0], market_name[0].upper(), 1)}",
                message=data,
            )
            # 불능 상태에서 저장된 메시지가 있는 경우 함께 전송
            while self.except_list[market_name]:
                stored_message = self.except_list[market_name].pop(0)
                await produce_sending(
                    topic=f"{symbol.lower()}SocketDataIn{market_name.replace(market_name[0], market_name[0].upper(), 1)}",
                    message=stored_message,
                )

        except KafkaConnectionError as error:
            await self.p.error_log(
                error_type="etc_error",
                message=f"broker 통신 불가로 임시 저장합니다 --> {error} data -> {len(self.except_list)}",
            )
            self.except_list[market_name].append(data)


class CoinStreamFacade:
    def __init__(self) -> None:
        self.kafka_sender = KafkaMessageSender()
        self.message_logger = MessageDataPreprocessing(self.kafka_sender)
        self.websocket_manager = WebsocketConnectionManager(self.message_logger)

    async def websocket_to_json(
        self, uri: str, subscribe_fmt: list[dict], symbol: str
    ) -> None:
        try:
            await self.websocket_manager.websocket_to_json(uri, subscribe_fmt, symbol)
        except Exception as error:
            print(error)
