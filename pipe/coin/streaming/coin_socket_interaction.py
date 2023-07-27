"""
COIN Streaming socket initialiation
"""
import json
import asyncio
from pathlib import Path
from typing import Any, Coroutine
from asyncio.exceptions import TimeoutError, CancelledError

from coin.core.data_mq.data_interaction import produce_sending
from coin.core.market.coin_abstract_class import CoinPresentPriceMarketPlace
from coin.core.settings.properties import market_setting
from coin.core.settings.create_log import log

import websockets

present_path = Path(__file__).parent
logger = log(f"{present_path}/log/worker.log", "worker")


class CoinPresentPriceWebsocket(CoinPresentPriceMarketPlace):
    """
    Coin Stream
    """

    def __init__(self) -> None:
        self.market_env = market_setting("socket")
        self.logger = log(f"{present_path}/log/worker.log", "worker")

    def create_logger(self, log_name: str):
        """
        주어진 이름으로 로거를 생성하는 함수.

        Args:
            log_name (str): 로거에 사용될 이름.

        Returns:
            logger: 주어진 이름으로 설정된 로거를 반환.
        """
        return log(f"{present_path}/streaming/log/{log_name}.log", log_name)

    async def put_message_to_queue(
        self, message: str, uri: str, queue: asyncio.Queue
    ) -> Coroutine[Any, Any, None]:
        """
        메시지를 로깅하고 큐에 넣는 함수.

        Args:
            message (str): 큐에 넣을 메시지.
            uri (str): 메시지와 연관된 URI.
            queue (asyncio.Queue): 메시지를 넣을 큐.
        """
        log_name: str = uri.split("//")[1].split(".")[1]
        logger = self.create_logger(log_name)

        logger.info(f"{message}")
        await produce_sending(topic=f"{log_name}_socket", message=message)
        await queue.put((uri, message))

    async def handle_message(
        self, websocket: Any, uri: str, queue: asyncio.Queue
    ) -> Coroutine[Any, Any, None]:
        """
        웹소켓에서 메시지를 지속적으로 받아 큐에 넣는 함수.

        Args:
            websocket (Any): 메시지를 받을 웹소켓.
            uri (str): 웹소켓과 연관된 URI.
            queue (asyncio.Queue): 메시지를 넣을 큐.
        """
        log_name: str = uri.split("//")[1].split(".")[1]

        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                await self.put_message_to_queue(message, uri, queue)
            except asyncio.TimeoutError:
                logger.error(f"Timeout while receiving from {uri}")
                await produce_sending(
                    topic=f"{log_name}_timeout", message={"timeout": uri}
                )

    async def websocket_to_json(
        self, uri: str, subscribe_fmt: list[dict], queue: asyncio.Queue
    ) -> Coroutine[Any, Any, None]:
        """
        웹소켓에 연결하고, 구독 데이터를 전송하고, 받은 메시지를 처리하는 함수.

        Args:
            uri (str): 연결할 URI.
            subscribe_fmt (list[dict]): 연결 후 전송할 데이터.
            queue (asyncio.Queue): 받은 메시지를 넣을 큐.
        """
        log_name: str = uri.split("//")[1].split(".")[1]
        logger = self.create_logger(log_name)

        async with websockets.connect(uri) as websocket:
            try:
                subscribe_data: str = json.dumps(subscribe_fmt)
                await websocket.send(subscribe_data)
                asyncio.sleep(1)

                message: str = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.info(f"Failed to parse message as JSON: {message}")

                match data:
                    case {"resmsg": "Connected Successfully"}:
                        logger.info(f"Connected to {uri}, {data}")
                    case {"event": "korbit:connected"}:
                        logger.info(f"Connected to {uri}, {data}")
                    case _:
                        logger.error("Not Found Market Connected")

                await self.handle_message(websocket, uri, queue)
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout while connecting to {uri}, Error: {e}")

    async def worker(self, input_queue: asyncio.Queue) -> None:
        """
        큐에서 메시지를 받는 함수

        Args:
            queue (asyncio.Queue): 메시지를 가져올 큐
        """

        while True:
            url, message = await input_queue.get()
            self.logger.info(f"Message from {url}: {message}")
            input_queue.task_done()

    async def coin_present_architecture(self) -> None:
        """
        웹소켓 연결 및 메시지 처리를 수행하는 메인 함수
        여기서 worker 함수를 통해 큐에서 메시지를 가져와 처리
        동시에 각각의 마켓에 연결하여 메시지를 받아옴
        """
        try:
            queue = asyncio.Queue()
            workers = [asyncio.create_task(self.worker(queue)) for _ in range(3)]

            coroutines: list[Any] = [
                self.market_env[i]["api"].get_present_websocket(queue)
                for i in self.market_env
            ]
            await asyncio.gather(*coroutines)

            await queue.join()
            for w in workers:
                w.cancel()
        except (TimeoutError, CancelledError) as e:
            self.logger.error("진행하지 못했습니다 --> %s", e)
