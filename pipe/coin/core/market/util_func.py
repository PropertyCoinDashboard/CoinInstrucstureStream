"""
유틸 함수
"""
import json
import asyncio
import configparser
from pathlib import Path
from typing import Any, Coroutine
from collections import defaultdict

import requests
import websockets
from coin.core.settings.create_log import SocketLogCustomer
from coin.core.data_mq.data_interaction import produce_sending


path = Path(__file__).parent
parser = configparser.ConfigParser()
parser.read(f"{path.parent}/config/urls.conf")

UPBIT_URL: str = parser.get("APIURL", "UPBIT")
BITHUMB_URL: str = parser.get("APIURL", "BITHUMB")
KORBIT_URL: str = parser.get("APIURL", "KORBIT")
COINONE_URL: str = parser.get("APIURL", "COINONE")
MAXLISTSIZE: int = 10


def header_to_json(url: str) -> Any:
    """
    json
    """
    headers: dict[str, str] = {"accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=60)

    match response.status_code:
        case 200:
            return response.json()
        case _:
            raise requests.exceptions.RequestException(
                f"API Request에 실패하였습니다 status code --> {response.status_code}"
            )


def get_symbol_collect_url(market: str) -> str:
    """URL matting

    Depandancy:
        -  possible python 3.10 \n
    Args:
        -  market (str): market name \n
    Raises:
        - ValueError: Not Fount market is ValueError string \n
    Returns:
        str: market url
    """
    match market:
        case "upbit":
            return UPBIT_URL
        case "bithum":
            return BITHUMB_URL
        case "korbit":
            return KORBIT_URL
        case "coinone":
            return COINONE_URL
        case _:
            raise ValueError("Not Found market")


def parse_uri(uri: str) -> str:
    """
    주어진 URI를 파싱해서 로그 이름을 반환하는 함수.

    Args:
        uri (str): 파싱할 URI.

    Returns:
        str: 로그 이름.
    """
    return uri.split("//")[1].split(".")[1]


class MarketPresentPriceWebsocket:
    """
    Coin Stream
    """

    def __init__(self) -> None:
        from coin.core.settings.properties import market_setting

        self.p = SocketLogCustomer()
        self.conn_logger = self.p.create_logger(
            log_name="price-data",
            exchange_name="total",
            log_type="price_data_counting",
        )
        self.error_logger = self.p.create_logger(
            log_name="error-logger",
            exchange_name="total",
            log_type="error_data_counting",
        )
        self.message_by_data = defaultdict(list)
        self.market = market_setting("socket")
        self.register_message = [
            "Filter Registered Successfully",
            "korbit:subscribe",
        ]

    async def get_register_connection(self, message: bytes | str, uri: str):
        """
        market websocket register

        Args:
            message (_type_): register message
        """
        log_name = parse_uri(uri)
        logger = self.p.create_logger(
            log_name=f"{log_name}-register",
            exchange_name=log_name,
            log_type="register",
        )
        logger.info(message)

    async def put_message_to_logging(
        self, message: str, uri: str, symbol: str
    ) -> Coroutine[Any, Any, None]:
        """
        메시지를 로깅하고 큐에 넣는 함수.

        Args:
            symbol (str): 심볼 메시지
            message (str): 큐에 넣을 메시지.
            uri (str): 메시지와 연관된 URI.
        """
        from coin.core.market.data_format import CoinMarketData

        log_name = parse_uri(uri)
        message = json.loads(message)

        # filter
        matches_all: bool = any(ignore in message for ignore in self.register_message)

        if matches_all:
            # register log만
            self.get_register_connection(message, uri=uri)
        else:
            try:
                # bithumb, korbit 특정 거래소에 대한 추가 처리
                if log_name == "bithumb":
                    message = message["content"]
                elif log_name == "korbit":
                    message = message["data"]

                time = message[self.market[log_name]["timestamp"]]
                parameter: list[str * 6] = list(self.market[log_name]["parameter"])
                schmea_key: dict[str, Any] = {
                    key: message[key] for key in message if key in parameter
                }

                # 스키마 통일화
                market_schema: str = CoinMarketData.from_api(
                    market=f"{log_name}-{symbol.upper()}",
                    time=time,
                    coin_symbol=symbol.upper(),
                    api=schmea_key,
                    data=parameter,
                ).model_dump(mode="json")

                self.message_by_data[log_name].append(market_schema)
                await self.message_kafka_sending(market_name=log_name, symbol=symbol)

                self.conn_logger.info(market_schema)
            except Exception as error:
                self.error_logger.error(
                    "Price Scoket Connection Error --> %s url --> %s", error, log_name
                )

    async def message_kafka_sending(
        self, market_name: str, symbol: str
    ) -> Coroutine[Any, Any, None]:
        """카프카 메시지 전송

        Args:
            market_name (str): 마켓이름
            symbol (str): 심볼이름

        Returns:
            Coroutine[Any, Any, None]: 코루틴으로 yield가 지속적으로 생성되니 어떠한 값이 들어올 줄 몰라 Any
        """

        # MAXLISTSIZE = 10
        if len(self.message_by_data[market_name]) >= MAXLISTSIZE:
            await produce_sending(
                topic=f"{symbol.lower()}SocketDataIn{market_name.replace(market_name[0], market_name[0].upper(), 1)}",
                message=self.message_by_data[market_name],
            )
            self.message_by_data[market_name]: list[market_name] = []

    async def handle_message(
        self, websocket: Any, uri: str, symbol: str
    ) -> Coroutine[Any, Any, None]:
        """
        Args:
            websocket (Any): 메시지를 받을 웹소켓.
            uri (str): 웹소켓과 연관된 URI.
            symbol (str): coin_symbol
        """
        log_name = parse_uri(uri)
        logger = self.p.create_logger(
            log_name=f"{log_name}not",
            exchange_name=log_name,
            log_type="not_connection",
        )

        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                await asyncio.sleep(1.0)
                await self.put_message_to_logging(message, uri, symbol=symbol)
            except asyncio.TimeoutError:
                logger.error(f"Timeout while receiving from {uri}")

    async def send_data(
        self, websocket: Any, subscribe_fmt: list[dict]
    ) -> Coroutine[Any, Any, None]:
        """
        소켓 인증하기 위한 절차 보내기

        Args:
            websocket (Any): 웹소켓
            subscribe_fmt (list[dict]): 소켓에 필요한 설정값들
        """
        subscribe_data: str = json.dumps(subscribe_fmt)
        await websocket.send(subscribe_data)
        await asyncio.sleep(2)

    async def handle_connection(
        self, websocket: Any, uri: str
    ) -> Coroutine[Any, Any, None]:
        """
        connection socket 마다 관리

        Args:
            websocket (Any): 소켓
            uri (str): 소켓주소

        Returns:
            Coroutine[Any, Any, None]: None
        """
        message: str = await asyncio.wait_for(websocket.recv(), timeout=30.0)
        data = json.loads(message)
        log_name = parse_uri(uri)
        logger = self.p.create_logger(
            log_name=f"{log_name}connect",
            exchange_name=log_name,
            log_type="connect",
        )

        match data:
            case {"resmsg": "Connected Successfully"}:
                logger.info(f"Connected to {uri}, {data}")
            case {"event": "korbit:connected"}:
                logger.info(f"Connected to {uri}, {data}")
            case _:
                logger.info(f"Connected to {uri}")

    async def websocket_to_json(
        self, uri: str, subscribe_fmt: list[dict], symbol: str
    ) -> Coroutine[Any, Any, None]:
        """
        웹소켓에 연결하고, 구독 데이터를 전송하고, 받은 메시지를 처리하는 함수.

        Args:
            uri (str): 연결할 URI.
            subscribe_fmt (list[dict]): 연결 후 전송할 데이터.
            queue (asyncio.Queue): 받은 메시지를 넣을 큐.
        """

        async with websockets.connect(uri) as websocket:
            try:
                await self.send_data(websocket, subscribe_fmt)
                await self.handle_connection(websocket, uri)
                await self.handle_message(websocket, uri, symbol=symbol)
            except asyncio.TimeoutError as error:
                self.error_logger.error(
                    "Timeout while connecting to %s, Error: %s", uri, error
                )


"""
리팩토링 준비 
1. 기능 분리 
2. 로깅 분리 
3. 정형화 

class ConnectionManager:
    async def send_data(self, websocket, subscribe_fmt):
        # ...

    async def handle_connection(self, websocket, uri):
        # ...

class MessageHandler:
    async def handle_message(self, websocket, uri, symbol):
        # ...

    async def put_message_to_logging(self, message, uri, symbol):
        # ...

class MarketPresentPriceWebsocket:
    # ...

    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.message_handler = MessageHandler()

"""
