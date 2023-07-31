"""
유틸 함수
"""
import json
import asyncio
import configparser
from pathlib import Path
from typing import Any, Coroutine

import requests
import websockets
from coin.core.settings.create_log import log


path = Path(__file__).parent
parser = configparser.ConfigParser()
parser.read(f"{path.parent}/config/urls.conf")

UPBIT_URL: str = parser.get("APIURL", "UPBIT")
BITHUMB_URL: str = parser.get("APIURL", "BITHUMB")
KORBIT_URL: str = parser.get("APIURL", "KORBIT")
COINONE_URL: str = parser.get("APIURL", "COINONE")


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

    def create_logger(self, log_name: str, exchange_name: str, log_type: str):
        """
        주어진 이름으로 로거를 생성하는 함수.

        Args:
            log_name (str): 로거에 사용될 이름.
            exchange_name (str): 거래소 이름.

        Returns:
            logger: 주어진 이름으로 설정된 로거를 반환.
        """
        try:
            return log(
                f"{path.parent.parent}/streaming/log/{exchange_name}/{exchange_name}_{log_type}.log",
                log_name,
            )
        except (FileNotFoundError, FileExistsError):
            a: Path = path.parent.parent / "streaming" / "log" / exchange_name
            a.mkdir()

    async def get_register_connection(self, message: bytes | str, uri: str):
        """
        market websocket register

        Args:
            message (_type_): register message
        """
        log_name = parse_uri(uri)
        logger = self.create_logger(
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
            queue (asyncio.Queue): 메시지를 넣을 큐.
        """
        from coin.core.settings.properties import market_setting
        from coin.core.market.data_format import CoinMarketData

        market: json = market_setting("socket")
        register_message = [
            "Filter Registered Successfully",
            "korbit:subscribe",
        ]
        # filter
        matches_all: bool = any(ignore in str(message) for ignore in register_message)

        if matches_all:
            # register log만
            await self.get_register_connection(message, uri=uri)
        else:
            try:
                log_name = parse_uri(uri)
                message = json.loads(message)
                conn_logger = self.create_logger(
                    log_name=f"{log_name}-data",
                    exchange_name=log_name,
                    log_type=f"_data_{symbol}",
                )
                # conn_logger.info(message)

                # bithumb, korbit 등 특정 거래소에 대한 추가 처리
                if log_name == "bithumb":
                    message = message["content"]
                elif log_name == "korbit":
                    message = message["data"]

                time = message[market[log_name]["timestamp"]]
                market_schema = CoinMarketData(
                    market=log_name,
                    time=time,
                    data={key: message[key] for key in market[log_name]["parameter"]},
                ).model_dump()

                # 변환된 메시지 로깅
                conn_logger.info(market_schema)
            except Exception as e:
                print(e)

    async def handle_message(
        self, websocket: Any, uri: str, symbol: str
    ) -> Coroutine[Any, Any, None]:
        """
        웹소켓에서 메시지를 지속적으로 받아 큐에 넣는 함수.

        Args:
            websocket (Any): 메시지를 받을 웹소켓.
            uri (str): 웹소켓과 연관된 URI.
            queue (asyncio.Queue): 메시지를 넣을 큐.
        """
        log_name = parse_uri(uri)
        logger = self.create_logger(
            log_name=f"{log_name}not",
            exchange_name=log_name,
            log_type="not_connection",
        )

        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                asyncio.sleep(100.0)
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
        asyncio.sleep(2)

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
        logger = self.create_logger(
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
        log_name = parse_uri(uri)
        logger = self.create_logger(
            log_name=f"{log_name}start",
            exchange_name=log_name,
            log_type="socket_start",
        )

        async with websockets.connect(uri) as websocket:
            try:
                await self.send_data(websocket, subscribe_fmt)
                await self.handle_connection(websocket, uri)
                await self.handle_message(websocket, uri, symbol=symbol)
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout while connecting to {uri}, Error: {e}")
