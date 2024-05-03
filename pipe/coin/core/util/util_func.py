"""
유틸 함수
"""

import requests
from typing import Any
from coin.core.setting.properties import (
    UPBIT_URL,
    BITHUMB_URL,
    KORBIT_URL,
    COINONE_URL,
    GOPAX_URL,
)
from coin.core.setting.properties import (
    SOCKET_UPBIT_URL,
    SOCKET_BITHUMB_URL,
    SOCKET_KORBIT_URL,
    SOCKET_COINONE_URL,
    SOCKET_GOPAX_URL,
)


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


def get_symbol_collect_url(market: str, type_: str) -> str:
    """URL matting

    Args:
        -  market (str): market name \n
        -  type_ (str): U Type \n
    Raises:
        - ValueError: Not Fount market is ValueError string \n
    Returns:
        str: market url
    """
    urls = {
        ("upbit", "socket"): SOCKET_UPBIT_URL,
        ("upbit", "rest"): UPBIT_URL,
        ("bithumb", "socket"): SOCKET_BITHUMB_URL,
        ("bithumb", "rest"): BITHUMB_URL,
        ("korbit", "socket"): SOCKET_KORBIT_URL,
        ("korbit", "rest"): KORBIT_URL,
        ("coinone", "socket"): SOCKET_COINONE_URL,
        ("coinone", "rest"): COINONE_URL,
        ("gopax", "socket"): SOCKET_GOPAX_URL,
        ("gopax", "rest"): GOPAX_URL,
    }

    url = urls.get((market, type_))
    if url is None:
        raise ValueError("등록되지 않은 거래소입니다.")
    return url


def market_name_extract(market: str) -> str:
    return market.replace(market[0], market[0].upper(), 1)
