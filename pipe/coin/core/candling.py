import time
import datetime
import requests
import pandas as pd
import plotly.graph_objects as go
from typing import Any, Optional
from coin.core.util.util_func import header_to_json, making_time, utc_to_unix_ms
from coin.core.setting.properties import UPBIT_URL, BITHUMB_URL, COINONE_URL


class ApiBasicArchitecture:
    """
    기본 클래스
    :param name -> 코인 이름
    :param date -> 날짜
    :param count -> data를 가져올 개수

    __namespace__
        -> coin symbol은 대문자로 취급하기에 소문자가 오더라도 upper로 오류방지
    """

    def __init__(
        self,
        name: str | None = None,
        date: datetime.datetime | None = None,
        count: int | None = None,
    ) -> None:
        self.name: str | None = name
        self.date: str | None = date
        self.count: int | None = count
        self.name_candle_count = f"market=KRW-{self.name}&count={self.count}"
        self.name_candle_count_date = (
            f"market=KRW-{self.name}&to={self.date}&count={self.count}"
        )

    def __namesplit__(self) -> str:
        return self.name.upper()


class UpBitCandlingAPI(ApiBasicArchitecture):
    """
    :param time
        minutes, days, weeks, year
        - 분, 일, 주, 년
    :param minit
        - 시간 단위
    :param count
        - 얼마나 가져올것인지
    :param date
        - 시간 단위
    """

    def upbit_candle_price(self, mint: int) -> list:
        return header_to_json(
            f"{UPBIT_URL}/candles/minutes/{mint}?{self.name_candle_count}"
        )

    # 상위 200개
    def upbit_candle_day_price(self) -> list:
        return header_to_json(f"{UPBIT_URL}/candles/days?{self.name_candle_count}")

    # 날짜 커스텀
    def upbit_candle_day_custom_price(self) -> list:
        return header_to_json(f"{UPBIT_URL}/candles/days?{self.name_candle_count_date}")


class BithumCandlingAPI(ApiBasicArchitecture):
    """
    :param minit
        - 차트 간격, 기본값 : 24h {1m, 3m, 5m, 10m, 30m, 1h, 6h, 12h, 24h 사용 가능}
    """

    # 시간별 통합으로 되어 있음
    def bithum_candle_price(self, mint: str) -> list:
        return header_to_json(f"{BITHUMB_URL}/candlestick/{self.name}_KRW/{mint}")


class CoinoneCandlingAPI(ApiBasicArchitecture):
    """
    :param minit
        -  차트 단위 1m, 3m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, 6h, 1d, 1w 허용값
    """

    # 시간별 통합으로 되어 있음
    def coinone_candle_price(self, mint: str) -> dict[str, Any]:
        return header_to_json(
            f"{COINONE_URL}/chart/KRW/{self.name}?interval={mint}&timestamp={self.date}"
        )


def api_injectional(
    api: Any, inject_parmeter: Any, coin_name: Optional[str] = None
) -> pd.DataFrame:
    # API 호출
    try:
        api_init = api

        api_init = pd.DataFrame(
            inject_parmeter,
            columns=[
                "timestamp",
                "opening_price",
                "trade_price",
                "high_price",
                "low_price",
                "candle_acc_trade_volume",
            ],
        )
        api_init["coin_symbol"] = coin_name
        api_init["timestamp"] = api_init["timestamp"].apply(
            lambda x: time.strftime(r"%Y-%m-%d %H:%M", time.localtime(x / 1000))
        )
        api_init["opening_price"] = api_init["opening_price"].apply(lambda x: float(x))
        api_init["trade_price"] = api_init["trade_price"].apply(lambda x: float(x))
        api_init["high_price"] = api_init["high_price"].apply(lambda x: float(x))
        api_init["low_price"] = api_init["low_price"].apply(lambda x: float(x))
        api_init["candle_acc_trade_volume"] = api_init["candle_acc_trade_volume"].apply(
            lambda x: float(x)
        )

        time_data = api_init["timestamp"].str.split(" ", expand=True)
        api_init["timestamp"] = time_data[0]

        return pd.DataFrame(api_init)
    except (AttributeError, KeyError):
        print("끝")


# 결과 출력하기
def upbit_trade_all_list(
    time_data: list[datetime.datetime], coin_name: Optional[str] = None
) -> list[pd.DataFrame]:
    timer: list[datetime.datetime] = time_data
    result_upbit_data: list[pd.DataFrame] = []

    for dt in timer:
        try:
            a = dt.strftime("%Y-%m-%d %H:%M:%S")

            upbit_init = UpBitCandlingAPI(
                name=coin_name, count=200, date=a
            ).upbit_candle_day_custom_price()

            # API 호출
            market_init = api_injectional(upbit_init, upbit_init, coin_name=coin_name)

            if market_init is None:
                continue

            result_upbit_data.append([market_init])
        except requests.exceptions.JSONDecodeError:
            continue

    return result_upbit_data


def coinone_trade_all_list(
    time_data: list[datetime.datetime], coin_name: Optional[str] = None
) -> list[pd.DataFrame]:
    result_coinone_data: list[pd.DataFrame] = []

    for a in time_data:
        try:
            # UTC 시간으로 변환
            utc_time = a.astimezone(datetime.timezone.utc)

            # UTC 시간을 Unix 시간 (ms)으로 변환
            unix_timestamp_ms = utc_to_unix_ms(utc_time)

            coinone_api = CoinoneCandlingAPI(name=coin_name, date=unix_timestamp_ms)
            candle_data = coinone_api.coinone_candle_price("1d")["chart"]
            result = pd.DataFrame(candle_data)
            if candle_data is None:
                continue

            result_coinone_data.append(result)
        except requests.exceptions.JSONDecodeError:
            print("error")

    return result_coinone_data


def transform_coinone_schema(data: pd.DataFrame, coin_name: str) -> pd.DataFrame:
    trans_data: pd.DataFrame = data.rename(
        columns={
            "open": "opening_price",
            "high": "high_price",
            "low": "low_price",
            "close": "trade_price",
            "target_volume": "candle_acc_trade_volume",
        }
    )

    trans_data["coin_symbol"] = coin_name
    trans_data["timestamp"] = trans_data["timestamp"].apply(
        lambda x: time.strftime(r"%Y-%m-%d", time.localtime(x / 1000))
    )
    trans_data["opening_price"] = trans_data["opening_price"].apply(lambda x: float(x))
    trans_data["trade_price"] = trans_data["trade_price"].apply(lambda x: float(x))
    trans_data["high_price"] = trans_data["high_price"].apply(lambda x: float(x))
    trans_data["low_price"] = trans_data["low_price"].apply(lambda x: float(x))
    trans_data["candle_acc_trade_volume"] = trans_data["candle_acc_trade_volume"].apply(
        lambda x: float(x)
    )

    return trans_data[
        [
            "coin_symbol",
            "timestamp",
            "opening_price",
            "trade_price",
            "high_price",
            "low_price",
            "candle_acc_trade_volume",
        ]
    ]


def bithum_trade_all_list(coin_name: Optional[str] = None) -> pd.DataFrame:
    bithum_init: list = BithumCandlingAPI(name=coin_name).bithum_candle_price(
        mint="24h"
    )
    bithum_init = api_injectional(bithum_init, bithum_init.get("data"), coin_name)
    return bithum_init


def trade_data_concat(data: list) -> pd.DataFrame:
    try:
        # 첫 번째 요소의 타입을 확인하여 중첩된 리스트인지 판별
        if isinstance(data[0], list):
            result_data = pd.concat([df for [df] in data], ignore_index=True)
        else:
            result_data = pd.concat([df for df in data], ignore_index=True)

        result_data = result_data.sort_values(by="timestamp", ascending=False)
        return result_data
    except ValueError as error:
        print(f"{data}를 합칠 수 없습니다. 비어 있거나 존재하지 않습니다. 에러 내용 --> ", error)
        return None


def coin_trading_data_concatnate(coin_name: str) -> list[dict[str, Any]]:
    bithum_init = bithum_trade_all_list(coin_name=coin_name)
    upbit_init = trade_data_concat(
        upbit_trade_all_list(coin_name=coin_name, time_data=making_time())
    )
    coinone_init = transform_coinone_schema(
        trade_data_concat(coinone_trade_all_list(making_time(), coin_name)), coin_name
    )

    merge_data: pd.DataFrame = (
        pd.concat([upbit_init, bithum_init, coinone_init], ignore_index=True)
        .groupby(["timestamp", "coin_symbol"])
        .mean()
        .reset_index()
    )
    return merge_data.to_dict(orient="records")


merged_data = coin_trading_data_concatnate("BTC")
bithum_init = BithumCandlingAPI(name="BTC").bithum_candle_price(mint="24h")
bithum_init = api_injectional(bithum_init, bithum_init.get("data"))
upbit_init = trade_data_concat(
    upbit_trade_all_list(coin_name="BTC", time_data=making_time())
)
coinone_init = transform_coinone_schema(
    trade_data_concat(coinone_trade_all_list(making_time(), "BTC")), "BTC"
)

fig = go.Figure(layout=go.Layout(title=go.layout.Title(text="Bitcoin -- BTC")))
fig.add_trace(
    go.Scatter(
        x=bithum_init["timestamp"],
        y=bithum_init["opening_price"],
        name="bithum",
        mode="lines",
    )
)
fig.add_trace(
    go.Scatter(
        x=upbit_init["timestamp"],
        y=upbit_init["opening_price"],
        name="upbit",
        mode="lines",
    )
)
fig.add_trace(
    go.Scatter(
        x=coinone_init["timestamp"],
        y=coinone_init["opening_price"],
        name="coinone",
        mode="lines",
    )
)
fig.show()
