import asyncio
from coin.core.coin_socket_interaction import CoinPresentPriceWebsocket


async def coin_present_websocket(symbol: str) -> None:
    await CoinPresentPriceWebsocket().coin_present_architecture(symbol)


if __name__ == "__main__":
    asyncio.run(coin_present_websocket("BTC"))
