# SparkStreamingProject


# architecture
## 실시간 코인 현재가 계산 
- REST API [upbit, bithumb, coinone, korbit] (BTC, ETH)
- Websocket [upbit, bithumb, korbit, (coinone 미지원)] (BTC, ETH)

### 기능 구현 실시간 kafka - spark streaming -> kafka 
- 실시간 코인 현재가 평균 계산
- 코인 심볼 추출
- 코인 {이름: 심볼} 4사 중복된 코인 합쳐서 추출 [추출된 기준 --> upbit]

### 디자인 패턴 
- websocket[추상화 패턴]
- restapi[추상화 패턴]

### 데이터 정형화 pydantic 사용
- opening_price 시가
- closeing_price 종가
- max_price 저가
- min_price 고가
- prev_closing_price 전일 종가
- acc_trade_volume_24h 24시간 거래량
```
{
    "market": "upbit-BTC",
    "time": 1689659170616,
    "coin_symbol": "BTC",
    "data": {
        "opening_price": 38761000.0,
	"closeing_price": 38761000.0,
        "high_price": 38828000.0,
        "low_price": 38470000.0,
        "prev_closing_price": 38742000.0,
        "acc_trade_volume_24h": 2754.0481778,
    },

} 
```

### 구현해볼만한것 
- 호가 매수 매도 추가
- API 모아서 ML
