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
from coin.core.data_mq.data_interaction import produce_sending


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


def parse_uri(uri: str):
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
        self.logger = log(f"{path.parent}/log/worker.log", "worker")

    def create_logger(self, log_name: str, exchange_name: str):
        """
        주어진 이름으로 로거를 생성하는 함수.

        Args:
            log_name (str): 로거에 사용될 이름.
            exchange_name (str): 거래소 이름.

        Returns:
            logger: 주어진 이름으로 설정된 로거를 반환.
        """
        return log(
            f"{path.parent.parent}/streaming/log/{exchange_name}.log",
            log_name,
        )

    async def put_message_to_queue(
        self, message: str, uri: str, queue: asyncio.Queue
    ) -> Coroutine[Any, Any, None]:
        """
        메시지를 로깅하고 큐에 넣는 함수.

        Args:
            message (str): 큐에 넣을 메시지.
            uri (str): 메시지와 연관된 URI.
            queue (asyncio.Queue): 메시지를 넣을 큐.
        """
        log_name = parse_uri(uri)
        logger = self.create_logger(log_name=log_name, exchange_name=log_name)

        logger.info(f"{message}")
        await produce_sending(topic=f"{log_name}_socket", message=message)
        await queue.put((uri, message))

    async def handle_message(
        self, websocket: Any, uri: str, queue: asyncio.Queue
    ) -> Coroutine[Any, Any, None]:
        """
        웹소켓에서 메시지를 지속적으로 받아 큐에 넣는 함수.

        Args:
            websocket (Any): 메시지를 받을 웹소켓.
            uri (str): 웹소켓과 연관된 URI.
            queue (asyncio.Queue): 메시지를 넣을 큐.
        """
        log_name = parse_uri(uri)
        logger = self.create_logger(log_name=log_name, exchange_name=log_name)

        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                await self.put_message_to_queue(message, uri, queue)
            except asyncio.TimeoutError:
                logger.error(f"Timeout while receiving from {uri}")

    async def send_data(
        self, websocket: Any, subscribe_fmt: list[dict]
    ) -> Coroutine[Any, Any, None]:
        """
        데이터 보내기

        Args:
            websocket (Any): 웹소켓
            subscribe_fmt (list[dict]): 소켓에 필요한 설정값들
        """
        subscribe_data: str = json.dumps(subscribe_fmt)
        await websocket.send(subscribe_data)
        asyncio.sleep(1)

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
        logger = self.create_logger(log_name=log_name, exchange_name=log_name)

        match data:
            case {"resmsg": "Connected Successfully"}:
                logger.info(f"Connected to {uri}, {data}")
            case {"event": "korbit:connected"}:
                logger.info(f"Connected to {uri}, {data}")
            case _:
                logger.error("Not Found Market Connected")

    async def websocket_to_json(
        self, uri: str, subscribe_fmt: list[dict], queue: asyncio.Queue
    ) -> Coroutine[Any, Any, None]:
        """
        웹소켓에 연결하고, 구독 데이터를 전송하고, 받은 메시지를 처리하는 함수.

        Args:
            uri (str): 연결할 URI.
            subscribe_fmt (list[dict]): 연결 후 전송할 데이터.
            queue (asyncio.Queue): 받은 메시지를 넣을 큐.
        """
        log_name = parse_uri(uri)
        logger = self.create_logger(log_name=log_name, exchange_name=log_name)

        async with websockets.connect(uri) as websocket:
            try:
                await self.send_data(websocket, subscribe_fmt)
                await self.handle_connection(websocket, uri)
                await self.handle_message(websocket, uri, queue)
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout while connecting to {uri}, Error: {e}")
