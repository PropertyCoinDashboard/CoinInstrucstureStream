"""
Coin async present price kafka data streaming 
"""
import asyncio
from pathlib import Path
from asyncio.exceptions import CancelledError
from typing import Any, Coroutine

from pydantic.errors import PydanticUserError
from pydantic_core._pydantic_core import ValidationError


from coin.core.market.data_format import CoinMarket, CoinMarketData
from coin.core.settings.properties import market_setting
from coin.core.settings.create_log import SocketLogCustomer
from coin.core.data_mq.data_interaction import produce_sending
from coin.streaming.java_code_intersection import kafka_sending

present_path = Path(__file__).parent


class CoinPresentPriceReponseAPI:
    """
    Coin present price market place
    """

    def __init__(self) -> None:
        self.market_env = market_setting("rest")
        self.logging = SocketLogCustomer()

    async def coin_present_architecture(
        self,
        market: str,
        time: str,
        coin_symbol: str,
        api: Any,
        data: tuple[str, str, str, str, str, str],
    ) -> Coroutine[Any, Any, dict[str, Any] | None]:
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
            api_response = api.get_coin_present_price(coin_name=coin_symbol.upper())
            market_time: int = api_response[time]

            return CoinMarketData.from_api(
                market=market,
                time=market_time,
                coin_symbol=coin_symbol,
                api=api_response,
                data=data,
            ).model_dump()
        except (PydanticUserError, ValidationError) as error:
            self.logging.error_log("Exception occurred: %s", error)

    async def __get_market_present_price(
        self, market: str, coin_symbol: str
    ) -> Coroutine[Any, Any, dict[str, Any] | None]:
        """
        Get market present price

        Args:
            market (str): market name
            coin_symbol (str): coin symbol

        Returns:
            str: market data as a string
        """
        market_info = self.market_env[market]
        return await self.coin_present_architecture(
            market=f"{market}-{coin_symbol.upper()}",
            coin_symbol=coin_symbol,
            time=market_info["timestamp"],
            api=market_info["api"],
            data=market_info["parameter"],
        )

    async def total_pull_request(self, coin_symbol: str, topic_name: str) -> None:
        """
        Total Pull request

        Args:
            coin_symbol (str): coin symbol
            topic_name (str): topic name
        """
        while True:
            # await asyncio.sleep(1)
            try:
                tasks: list[Coroutine[Any, Any, dict[str, Any]]] = [
                    self.__get_market_present_price(
                        market=market, coin_symbol=coin_symbol
                    )
                    for market in self.market_env
                ]
                market_result = await asyncio.gather(*tasks, return_exceptions=True)
                # 스키마 정의
                schema: dict[str, dict[str, Any]] = CoinMarket(
                    **dict(zip(self.market_env.keys(), market_result))
                ).model_dump(mode="json")
                print(schema)
                await kafka_sending(topic_name, message=schema)
            except (TimeoutError, CancelledError, ValidationError) as error:
                self.logging.error_log("Data transmission failed: %s", error)
