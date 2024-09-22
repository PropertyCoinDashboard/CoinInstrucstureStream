"""
Coin async present price kafka data streaming 
"""

import logging
import datetime
import asyncio

from typing import Any
from common.core.types import KoreaCoinMarketData, ExchangeData
from common.utils.logger import AsyncLogger

from pydantic.errors import PydanticUserError
from pydantic import ValidationError

from korea_exchange.driver.rest_korea_exchange import UpbitRest
from korea_exchange.config.json_param_load import load_json
from korea_exchange.util.data_format import CoinMarket, CoinMarketData

# from coin.core.data_mq.data_interaction import KafkaMessageSender


class CoinPresentPriceReponseAPI:
    """
    Coin present price market place
    """

    def __init__(self) -> None:
        self.market_env = load_json("rest")
        self.logging = AsyncLogger(target="rest", log_file="rest.log")

    async def _coin_present_architecture(
        self,
        market: str,
        coin_symbol: str,
        api: Any,
        data: tuple[str],
    ) -> ExchangeData | None:
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
            api_response = await api.get_coin_all_info_price(
                coin_name=coin_symbol.upper()
            )
            return CoinMarketData.from_api(
                market=market,
                coin_symbol=coin_symbol,
                api=api_response,
                data=data,
            ).model_dump()
        except (PydanticUserError, ValidationError) as error:
            self.logging.log_message_sync(logging.ERROR, error)

    async def _get_market_present_price(
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
        market_data_architecture = await self._coin_present_architecture(
            market=f"{market}-{coin_symbol.upper()}",
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
            api_response_time = await UpbitRest().get_coin_all_info_price(
                coin_name=coin_symbol.upper()
            )
            api_response_time = api_response_time["timestamp"]
            # 밀리초를 초 단위로 변환
            timestamp_s = api_response_time / 1000

            # UTC 시간대에서 타임스탬프로 datetime 객체 생성
            dt_utc = datetime.datetime.fromtimestamp(
                timestamp_s, tz=datetime.timezone.utc
            )

            # "년-월-일 시:분:초" 형식으로 출력
            formatted_time = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
            await asyncio.sleep(1)
            try:
                tasks: list = [
                    self._get_market_present_price(
                        market=market, coin_symbol=coin_symbol
                    )
                    for market in self.market_env
                ]
                market_result = await asyncio.gather(*tasks, return_exceptions=True)

                # 스키마 정의
                schema: KoreaCoinMarketData = CoinMarket(
                    timestamp=api_response_time,
                    **dict(zip(self.market_env.keys(), market_result)),
                ).model_dump()
                # user_ids = random.randint(1, 5)  # 1에서 100 사이의 랜덤 번호를 생성

                # await KafkaMessageSender().produce_sending(
                #     message=schema,
                #     key=f"Total_{user_ids}",
                #     market_name="Total",
                #     symbol=coin_symbol,
                #     type_="RestDataIn",
                # )

                self.logging.log_message_sync(logging.INFO, message=schema)
            except Exception as error:
                await self.logging.log_message_sync(
                    logging.ERROR, f"Data transmission failed: {error}"
                )
                continue
