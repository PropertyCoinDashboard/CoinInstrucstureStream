import asyncio
from coin.core.coin_socket_interaction import CoinPresentPriceWebsocket


async def coin_present_websocket_btc() -> None:
    await CoinPresentPriceWebsocket().coin_present_architecture("SHIB")


async def coin_present_websocket_eth() -> None:
    await CoinPresentPriceWebsocket().coin_present_architecture("ETH")


async def coin_present_websocket() -> None:
    task = [
        asyncio.create_task(coin_present_websocket_btc()),
        asyncio.create_task(coin_present_websocket_eth()),
    ]
    await asyncio.gather(*task, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(coin_present_websocket_btc())
