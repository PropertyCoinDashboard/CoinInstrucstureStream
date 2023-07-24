"""
유틸 함수
"""
import json
from pathlib import Path
from typing import Any
import configparser

import requests
import websockets


path = Path(__file__).parent.parent
parser = configparser.ConfigParser()
parser.read(f"{path}/config/urls.conf")

UPBIT_URL: str = parser.get("APIURL", "UPBIT")
BITHUMB_URL: str = parser.get("APIURL", "BITHUMB")
KORBIT_URL: str = parser.get("APIURL", "KORBIT")
COINONE: str = parser.get("APIURL", "COINONE")

# 빗썸
# wss://pubwss.bithumb.com/pub/ws
# {"type": "ticker", "symbols": ["BTC_KRW", "ETH_KRW"], "tickTypes": ["MID"]}
# 현재가: {'status': '0000', 'resmsg': 'Connected Successfully'}
# 현재가: {'status': '0000', 'resmsg': 'Filter Registered Successfully'}

# 업비트
# "wss://api.upbit.com/websocket/v1"
# [
#     {"ticket": "UNIQUE_TICKET"},
#     {"type": "ticker", "codes": ["KRW-BTC"],
#       "isOnlyRealtime": True},
# ]

# 코빗
# wss://ws.korbit.co.kr/v1/user/push
# {
#     "accessToken": null,
#     "timestamp": 1558590089274,
#     "event": "korbit:subscribe",
#     "data": {"channels": ["ticker:btc_krw"]},
# }
# 현재가: {'timestamp': 1690217479348, 'key': 0, 'event': 'korbit:connected', 'data': {}}
# 현재가: {'timestamp': 1558590089274, 'event': 'korbit:subscribe', 'data': {'channels': ['ticker:btc_krw,eth_krw,xrp_krw']}}


async def websocket_to_json(uri: str, subscribe_fmt: list[dict]):
    """websocket json

    Args:
        uri (str): websocket uri
        subscribe_fmt (list[dict]): parameter
    """
    async with websockets.connect(uri) as websocket:
        subscribe_data = json.dumps(subscribe_fmt)
        await websocket.send(subscribe_data)

        data = await websocket.recv()
        data = json.loads(data)
        print(data)
        return data


def header_to_json(url: str) -> Any:
    """
    json
    """
    headers: dict[str, str] = {"accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=60)

    if response.status_code == 200:
        return response.json()

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
