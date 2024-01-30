"""
유틸 함수
"""

import requests
from datetime import datetime
from typing import Any
from coin.core.setting.properties import (
    UPBIT_URL,
    BITHUMB_URL,
    KORBIT_URL,
    COINONE_URL,
)


# UTC 시간을 Unix 시간 (ms)으로 변환하는 함수
def utc_to_unix_ms(utc_datetime: str) -> int:
    return int(utc_datetime.timestamp() * 1000)


def making_time() -> list:
    # 현재 시간 구하기
    now = datetime.datetime.now()

    # 목표 날짜 구하기
    # 현재 시간으로부터 200일씩 뒤로 가면서 datetime 객체 생성하기
    target_date = datetime.datetime(2013, 12, 27, 0, 0, 0)
    result = []
    while now >= target_date:
        result.append(now)
        now -= datetime.timedelta(days=200)
    return result


def parse_uri(uri: str) -> str:
    """
    주어진 URI를 파싱해서 로그 이름을 반환하는 함수.

    Args:
        uri (str): 파싱할 URI.

    Returns:
        str: 로그 이름.
    """
    return uri.split("//")[1].split(".")[1]


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


def market_name_extract(market: str) -> str:
    return market.replace(market[0], market[0].upper(), 1)
