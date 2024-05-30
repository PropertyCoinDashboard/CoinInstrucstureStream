"""
Coin async present price kafka data streaming 
"""

import asyncio
from asyncio.exceptions import CancelledError

from pathlib import Path
from typing import Any, Coroutine
from .util._typing import TotalCoinMarketData

from pydantic.errors import PydanticUserError
from pydantic_core._pydantic_core import ValidationError


from coin.core.abstract.ubkc_market_abstract import CoinSocketAndRestAbstract
from coin.core.setting.factory_api import load_json
from coin.core.util.data_format import CoinMarket, CoinMarketData
from coin.core.util.create_log import SocketLogCustomer
from coin.core.data_mq.data_interaction import KafkaMessageSender


present_path = Path(__file__).parent


class CoinPresentPriceReponseAPI:
    """
    Coin present price market place
    """

    def __init__(self) -> None:
        self.market_env = load_json("rest")
        self.logging = SocketLogCustomer(
            base_path=Path(__file__).parent, file_name="data", object_name="rest"
        )

    async def __coin_present_architecture(
        self,
        market: str,
        coin_symbol: str,
        time: int,
        api: CoinSocketAndRestAbstract,
        data: tuple[str],
    ) -> dict[str, Any] | None:
        """
        Coin present price architecture

        Args:
            market (str): marketname-coinsymbol
            coin_symbol (str): coinsymbol("BTC".."EHT"...)
            api (Any): coin_apis.py in class
            parameter (tuple[str * 6]): search parameter

        Returns:
            CoinMarketData: pydantic in JSON transformation
        """
        try:
            api_response = api.get_coin_all_info_price(coin_name=coin_symbol.upper())
            # market_time = int(datetime.datetime.now().timestamp())
            market_time: int = api_response[time]
            return CoinMarketData.from_api(
                market=market,
                time=market_time,
                coin_symbol=coin_symbol,
                api=api_response,
                data=data,
            ).model_dump()
        except (PydanticUserError, ValidationError) as error:
            self.logging.error_log("error", "Exception occurred: %s", error)

    async def __get_market_present_price(
        self, market: str, coin_symbol: str
    ) -> dict[str, Any] | None:
        """
        Get market present price

        Args:
            market (str): market name
            coin_symbol (str): coin

        Returns:
            str: market data as a string
        """
        market_info = self.market_env[market]
        market_data_architecture = await self.__coin_present_architecture(
            market=f"{market}-{coin_symbol.upper()}",
            time=market_info["timestamp"],
            coin_symbol=coin_symbol,
            api=market_info["api"],
            data=market_info["parameter"],
        )
        return market_data_architecture

    async def total_pull_request(self, coin_symbol: str) -> None:
        """
        Total Pull request

        Args:
            coin_symbol (str): coin symbol
            topic_name (str): topic name
        """
        while True:
            await asyncio.sleep(1)
            try:
                tasks: list = [
                    self.__get_market_present_price(
                        market=market, coin_symbol=coin_symbol
                    )
                    for market in self.market_env
                ]
                market_result = await asyncio.gather(*tasks, return_exceptions=True)
                # 스키마 정의
                schema: TotalCoinMarketData = CoinMarket(
                    **dict(zip(self.market_env.keys(), market_result))
                ).model_dump()

                await KafkaMessageSender().produce_sending(
                    message=schema,
                    market_name="Total",
                    symbol=coin_symbol,
                    type_="RestDataIn",
                )

                await self.logging.data_log(exchange_name="Total", message=schema)
            except (TimeoutError, CancelledError, ValidationError) as error:
                await self.logging.error_log(
                    "error", "Data transmission failed: %s", error
                )


# [
#     {
#         "market": "upbit-BTC",
#         "time": 1717056305638,
#         "coin_symbol": "BTC",
#         "data": {
#             "opening_price": Decimal("93910000.000"),
#             "trade_price": Decimal("94262000.000"),
#             "max_price": Decimal("94750000.000"),
#             "min_price": Decimal("93620000.000"),
#             "prev_closing_price": Decimal("93910000.000"),
#             "acc_trade_volume_24h": Decimal("2706.340"),
#         },
#     },
#     {
#         "market": "bithumb-BTC",
#         "time": 1717056306709,
#         "coin_symbol": "BTC",
#         "data": {
#             "opening_price": Decimal("93701000.000"),
#             "trade_price": Decimal("94185000.000"),
#             "max_price": Decimal("94724000.000"),
#             "min_price": Decimal("93280000.000"),
#             "prev_closing_price": Decimal("93701000.000"),
#             "acc_trade_volume_24h": Decimal("792.273"),
#         },
#     },
#     {
#         "market": "korbit-BTC",
#         "time": 1717056300875,
#         "coin_symbol": "BTC",
#         "data": {
#             "opening_price": Decimal("93992000.000"),
#             "trade_price": Decimal("94224000.000"),
#             "max_price": Decimal("94651000.000"),
#             "min_price": Decimal("93100000.000"),
#             "prev_closing_price": Decimal("94224000.000"),
#             "acc_trade_volume_24h": Decimal("35.386"),
#         },
#     },
#     {
#         "market": "coinone-BTC",
#         "time": 1717056306185,
#         "coin_symbol": "BTC",
#         "data": {
#             "opening_price": Decimal("93999000.000"),
#             "trade_price": Decimal("94236000.000"),
#             "max_price": Decimal("94696000.000"),
#             "min_price": Decimal("93100000.000"),
#             "prev_closing_price": Decimal("94000000.000"),
#             "acc_trade_volume_24h": Decimal("144.816"),
#         },
#     },
#     {
#         "market": "gopax-BTC",
#         "time": 1717022495000,
#         "coin_symbol": "BTC",
#         "data": {
#             "opening_price": Decimal("94500000.000"),
#             "trade_price": Decimal("94554000.000"),
#             "max_price": Decimal("94396000.000"),
#             "min_price": Decimal("94554000.000"),
#             "prev_closing_price": Decimal("69642625.142"),
#             "acc_trade_volume_24h": Decimal("0.753"),
#         },
#     },
# ]
