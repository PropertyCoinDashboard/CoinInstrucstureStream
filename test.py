import websocket
import json
import uuid
import time


def on_message(ws, message):
    data = json.loads(message)
    print(data)


def on_connect(ws):
    print("연결되었습니다!")
    # 연결 이후 BTC의 현재가 정보를 요청합니다.
    payload = [
        {"ticket": str(uuid.uuid4())},  # 요청자를 식별하는 랜덤한 UUID 생성
        {"type": "ticker", "codes": ["KRW-BTC"]},
    ]
    ws.send(json.dumps(payload))


def on_error(ws, error):
    print(f"에러 발생: {error}")


def on_close(ws, close_status_code, close_msg):
    print("연결이 종료되었습니다.")


def run_websocket():
    while True:
        ws_app = websocket.WebSocketApp(
            "wss://api.upbit.com/websocket/v1",
            on_message=on_message,
            on_open=on_connect,
            on_error=on_error,
            on_close=on_close,
        )
        ws_app.run_forever()
        # 2초 간격으로 재연결
        time.sleep(2)


if __name__ == "__main__":
    run_websocket()
