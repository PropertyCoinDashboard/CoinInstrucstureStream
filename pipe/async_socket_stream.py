from coin.streaming.coin_socket_interaction import CoinPresentPriceWebsocket
from concurrent.futures import ThreadPoolExecutor
import asyncio


async def coin_price_streaming():
    coin_present_price_websocket = CoinPresentPriceWebsocket()
    while True:
        await coin_present_price_websocket.coin_present_architecture()


if __name__ == "__main__":
    asyncio.run(coin_price_streaming())
