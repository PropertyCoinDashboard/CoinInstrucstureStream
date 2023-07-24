"""
유틸 함수
"""
from pathlib import Path
from typing import Any
import configparser

import requests


path = Path(__file__).parent.parent
parser = configparser.ConfigParser()
parser.read(f"{path}/config/urls.conf")

UPBIT_URL: str = parser.get("APIURL", "UPBIT")
BITHUMB_URL: str = parser.get("APIURL", "BITHUMB")
KORBIT_URL: str = parser.get("APIURL", "KORBIT")
COINONE: str = parser.get("APIURL", "COINONE")


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
