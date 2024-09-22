import logging
import tracemalloc
import asyncio
from asyncio.exceptions import CancelledError

import json
import websockets

from common.utils.logger import AsyncLogger
from common.core.abstract import (
    MessageDataPreprocessingAbstract,
    WebsocketConnectionAbstract,
)
from common.core.types import (
    SubScribeFormat,
    ExchangeData,
    ExchangeResponseData,
    PriceData,
)
from korea_exchange.config.json_param_load import load_json
from korea_exchange.util.data_format import CoinMarketData


class WebsocketConnectionManager(WebsocketConnectionAbstract):
    """웹소켓 승인 전송 로직"""

    def __init__(self) -> None:
        self.message_preprocessing = MessageDataPreprocessing()
        self._logger = AsyncLogger(target="socket", log_file="socket.log")

    async def socket_param_send(
        self, websocket: websockets, subs_fmt: SubScribeFormat
    ) -> None:
        """socket 통신 요청 파라미터 보내는 메서드
        Args:
            websocket: 소켓 연결
            subs_fmt: 웹소켓 승인 스키마
        """
        sub = json.dumps(subs_fmt)
        await websocket.send(sub)

    async def handle_connection(self, websocket: websockets, uri: str) -> None:
        """웹 소켓 커넥션 확인 함수
        Args:
            websocket: 소켓 연결
            uri: 각 uri들
        """
        message: str = await asyncio.wait_for(websocket.recv(), timeout=30.0)
        data = json.loads(message)
        market: str = uri.split("//")[1].split(".")[1]
        if data:
            self._logger.log_message_sync(logging.INFO, f"{market} 연결 완료")

    async def handle_message(
        self, websocket: websockets, uri: str, symbol: str
    ) -> None:
        """메시지 처리하는 메서드"""
        while True:
            try:
                message: ExchangeResponseData = await asyncio.wait_for(
                    websocket.recv(), timeout=30.0
                )
                await self.message_preprocessing.put_message_to_logging(
                    message, uri, symbol
                )
                await self.message_preprocessing.message_consumer()
                await asyncio.sleep(1.0)

            except Exception as error:
                self._logger.log_message_sync(
                    logging.ERROR,
                    message=f"{uri}에서 수신 중 타임아웃 발생 --> {error}",
                )

    async def websocket_to_json(
        self, uri: str, subs_fmt: SubScribeFormat, symbol: str
    ) -> None:
        """말단 소켓 시작 지점
        Args:
            uri: 소켓을 지원하는 uri
            subs_fmt: 웹소켓 승인 스키마
            symbol: 코인 심볼
        """
        async with websockets.connect(
            uri, ping_interval=30, ping_timeout=60
        ) as websocket:
            try:
                await self.socket_param_send(websocket, subs_fmt)
                await self.handle_connection(websocket, uri)
                await self.handle_message(websocket, uri, symbol)
            except websockets.exceptions.ConnectionClosedError as e:
                self._logger.log_message_sync(logging.ERROR, f"커넥션 에러 입니다: {e}")
                await asyncio.sleep(5)  # 재연결 전에 5초 대기
            except asyncio.TimeoutError as e:
                self._logger.log_message_sync(logging.ERROR, f"타임 에러 입니다: {e}")
                await asyncio.sleep(5)  # 타임아웃 후 5초 대기 후 재연결


class MessageDataPreprocessing(MessageDataPreprocessingAbstract):
    def __init__(self) -> None:
        self._logger = AsyncLogger(target="prepro", log_file="message.log")
        self.async_q = asyncio.Queue()
        self.market = load_json("socket")

    def process_exchange(self, market: str, message: dict) -> dict:
        """message 필터링
        Args:
            market: 거래소
            message: 데이터
        Returns:
            dict: connection 거친 후 본 데이터
        """
        # 거래소별 필터링 규칙 정의
        # fmt: off
        filters = {
            "coinone": lambda msg: msg.get("response_type") != "SUBSCRIBED" and msg.get("data"),
        }
        # 해당 거래소에 대한 필터가 정의되어 있는지 확인
        filter_function = filters.get(market)
        if filter_function:
            result = filters[market](message)
            if result:
                return result
        return message

    # fmt: off
    async def process_message(self, market: str, message: ExchangeResponseData, symbol: str) -> ExchangeData:
        """전처리 클래스
        Args:
            market: 거래소 이름
            message: 송신된 소켓 데이터
            symbol: 코인심볼
        """

        parameter: list = list(self.market[market]["parameter"])
        schema_key: PriceData = {
            key: message[key] for key in message if key in parameter
        }
        return CoinMarketData.from_api(
            market=f"{market}-{symbol.upper()}",
            coin_symbol=symbol.upper(),
            api=schema_key,
            data=parameter,
        ).model_dump(mode="json")
    
    async def put_message_to_logging(self, message: ExchangeResponseData, uri: str, symbol: str) -> None:
        """메시지 로깅"""
        market: str = uri.split("//")[1].split(".")[1]
        p_message: dict = self.process_exchange(market, json.loads(message))
        await self.async_q.put((uri, market, p_message, symbol))
        
    async def message_consumer(self) -> None:
        """메시지 소비"""
        uri, market, message, symbol = await self.async_q.get()

        try:            
            market_schema: dict = await self.process_message(market, message, symbol)
            # self.message_by_data[market].append(market_schema)
            # if len(self.message_by_data[market]) >= MAXLISTSIZE:
            #     await KafkaMessageSender().produce_sending(
            #         message=self.message_by_data[market],
            #         market_name=market_name_extract(market),
            #         symbol=symbol,
            #         type_="SocketDataIn",
            #     )
            #     self.message_by_data[market] = []

            parse_uri: str = uri.split("//")[1].split(".")[1]
            self._logger.log_message_sync(
                logging.INFO, message=f"{parse_uri} -- {market_schema}"
            )
        except (TypeError, KeyError) as error:
            pass
        except CancelledError:
            self._logger.log_message_sync(
                logging.ERROR,
                message=f"가격 소켓 연결 오류 --> {error} url --> {market}",
            )


class CoinPresentPriceWebsocket:
    """Coin Stream"""

    def __init__(
        self, symbol: str, market: str = "all", market_type: str = "socket"
    ) -> None:
        """socket 시작
        Args:
            symbol: 긁어올 코인
            market: 활성화할 마켓. Defaults to "all"이면 모든 거래소 선택.
            market_type: Defaults to "socket".
        """
        tracemalloc.start()
        self.market = market
        self.symbol = symbol
        self.market_env = load_json(market_type)
        self.logger = AsyncLogger(target="socket", log_file="connect.log")

    async def select_websocket(self) -> list:
        """마켓 선택"""
        parameter = self.market_env
        match self.market:
            case "all":
                return [
                    parameter[i]["api"].get_present_websocket(self.symbol)
                    for i in parameter
                ]
            case _:
                return [
                    parameter[self.market]["api"].get_present_websocket(self.symbol)
                ]

    async def coin_present_architecture(self) -> None:
        """실행 지점"""
        try:
            coroutines: list = await self.select_websocket()
            await asyncio.gather(*coroutines, return_exceptions=False)
        except (TimeoutError, CancelledError) as error:
            self.logger.log_message_sync(
                logging.ERROR, message=f"진행하지 못했습니다 --> {error}"
            )
