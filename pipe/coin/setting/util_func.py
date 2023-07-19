import requests
from typing import Any
from .properties import UPBIT_URL, BITHUMB_URL, KORBIT_URL


# JSON response
def header_to_json(url: str) -> Any:
    headers: dict[str, str] = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

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
        case _:
            raise ValueError("Not Found market")
