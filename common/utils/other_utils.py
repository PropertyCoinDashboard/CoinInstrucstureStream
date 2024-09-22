from common.setting.properties import (
    SOCKET_UPBIT_URL,
    SOCKET_BITHUMB_URL,
    SOCKET_COINONE_URL,
)
from common.setting.properties import (
    REST_UPBIT_URL,
    REST_BITHUMB_URL,
    REST_COINONE_URL,
    REST_KORBIT_URL,
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
        ("upbit", "rest"): REST_UPBIT_URL,
        ("bithumb", "socket"): SOCKET_BITHUMB_URL,
        ("bithumb", "rest"): REST_BITHUMB_URL,
        # ("korbit", "socket"): SOCKET_KORBIT_URL,
        ("korbit", "rest"): REST_KORBIT_URL,
        ("coinone", "socket"): SOCKET_COINONE_URL,
        ("coinone", "rest"): REST_COINONE_URL,
    }

    url = urls.get((market, type_))
    if url is None:
        raise ValueError("등록되지 않은 거래소입니다.")
    return url
