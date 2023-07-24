from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict
import json
import websockets


app = FastAPI()
templates = Jinja2Templates(directory="/code/app/templates")


class PriceData(BaseModel):
    opening_price: float
    max_price: float
    min_price: float
    prev_closing_price: float
    acc_trade_volume_24h: float


class AveragePrice(BaseModel):
    name: str
    time: int
    data: PriceData


class Message(BaseModel):
    average_price: AveragePrice


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            message_data = await websocket.receive_text()
            await websocket.send_json(message_data)
            await websocket.send_text(f"서버에서 받은 메시지: {message_data}")
        except Exception as e:
            # 연결이 끊어지거나 오류가 발생한 경우 처리합니다.
            print(f"WebSocket 오류: {e}")
            break


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
