import asyncio
from typing import Coroutine, NoReturn, Any
from coin.streaming.coin_socket_interaction import CoinPresentPriceWebsocket


async def coin_price_streaming() -> Coroutine[Any, Any, NoReturn]:
    coin_present_price_websocket = CoinPresentPriceWebsocket()
    await coin_present_price_websocket.coin_present_architecture("BTC")


if __name__ == "__main__":
    asyncio.run(coin_price_streaming())
