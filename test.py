import asyncio
import json
import uuid
import websockets


async def upbit_ws_client():
    uri = "wss://pubwss.bithumb.com/pub/ws"

    async with websockets.connect(uri) as websocket:
        subscribe_fmt = {
            "type": "ticker",
            "symbols": ["BTC_KRW", "ETH_KRW"],
            "tickTypes": ["MID"],
        }

        subscribe_data = json.dumps(subscribe_fmt)
        await websocket.send(subscribe_data)

        while True:
            data = await websocket.recv()
            asyncio.sleep(1)
            data = json.loads(data)
            print(f"현재가: {data}")


if __name__ == "__main__":
    asyncio.run(upbit_ws_client())
