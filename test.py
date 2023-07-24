import asyncio
import json
import uuid
import websockets


async def send_message(websocket):
    payload = [
        {"ticket": str(uuid.uuid4())},
        {"type": "ticker", "codes": ["KRW-BTC"]},
    ]
    await websocket.send(json.dumps(payload))


async def receive_message(websocket):
    while True:
        message = await websocket.recv()
        data = json.loads(message)
        print(data)


async def websocket_handler():
    uri = "wss://api.upbit.com/websocket/v1"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("연결되었습니다!")
                await asyncio.gather(
                    send_message(websocket), receive_message(websocket)
                )
        except Exception as e:
            print(f"에러 발생: {e}")
            await asyncio.sleep(2)  # 2초 간격으로 재연결


if __name__ == "__main__":
    asyncio.run(websocket_handler())
