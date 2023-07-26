from coin.streaming.coin_socket_interaction import CoinPresentPriceWebsocket
from concurrent.futures import ThreadPoolExecutor
import asyncio


async def test():
    coin_present_price_websocket = CoinPresentPriceWebsocket()
    while True:
        await coin_present_price_websocket.coin_present_architecture()
        print(await coin_present_price_websocket.coin_present_architecture())


if __name__ == "__main__":
    asyncio.run(test())
