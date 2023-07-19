from coin_interaction import CoinPresentPriceMarketPlace
import asyncio


async def btc_present_start():
    while True:
        await CoinPresentPriceMarketPlace.total_full_request("BTC")
        await asyncio.sleep(1)


async def eth_present_start():
    while True:
        await CoinPresentPriceMarketPlace.total_full_request("ETC")
        await asyncio.sleep(1)


async def be_present_gether():
    tasks = [
        asyncio.create_task(btc_present_start()),
        asyncio.create_task(eth_present_start()),
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


asyncio.run(be_present_gether())
