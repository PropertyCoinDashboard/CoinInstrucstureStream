"""
유틸 함수
"""
import json
import asyncio
import configparser
from typing import Any
from pathlib import Path

from coin.core.settings.create_log import log

import requests
import websockets


path = Path(__file__).parent
parser = configparser.ConfigParser()
parser.read(f"{path.parent}/config/urls.conf")

UPBIT_URL: str = parser.get("APIURL", "UPBIT")
BITHUMB_URL: str = parser.get("APIURL", "BITHUMB")
KORBIT_URL: str = parser.get("APIURL", "KORBIT")
COINONE: str = parser.get("APIURL", "COINONE")


async def handle_message(websocket: Any, uri: str, queue: asyncio.Queue):
    """비동기 큐 삽입구

    Args:
        websocket (Any): 소켓 입력값
        uri (str): 소켓 주소
        queue (asyncio.Queue): 큐
    """
    log_name: str = uri.split("//")[1].split(".")[1]
    logger = log(f"{path.parent.parent}/streaming/log/{log_name}.log", log_name)
    while True:
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            logger.info(f"{message}")
            await queue.put((uri, message))  # put message into the queue
        except asyncio.TimeoutError:
            logger.error(f"Timeout while receiving from {uri}")
            break


async def websocket_to_json(
    uri: str, subscribe_fmt: list[dict], queue: asyncio.Queue
) -> None:
    """비동기 요청

    Args:
        uri (str): 소켓 주소
        subscribe_fmt (list[dict]): 소켓에 필요한 설정
        queue (asyncio.Queue): 큐
    """
    log_name: str = uri.split("//")[1].split(".")[1]
    logger = log(f"{path.parent.parent}/streaming/log/{log_name}.log", log_name)
    async with websockets.connect(uri) as websocket:
        try:
            subscribe_data: str = json.dumps(subscribe_fmt)
            await websocket.send(subscribe_data)

            message: str = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                logger.info(f"Failed to parse message as JSON: {message}")

            match data:
                case {"resmsg": "Connected Successfully"}:
                    logger.info(f"Connected to {uri}, {data}")
                case {"event": "korbit:connected"}:
                    logger.info(f"Connected to {uri}, {data}")
                case _:
                    logger.error("Not Found Market Connected")

            await handle_message(websocket, uri, queue)
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout while connecting to {uri}, Error: {e}")


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


# 반복 호출 줄이기 위해..
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
            return COINONE
        case _:
            raise ValueError("Not Found market")
