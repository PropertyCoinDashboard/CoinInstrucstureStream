from dataclasses import dataclass


@dataclass(frozen=True)
class CoinSymbol:
    coin_symbol: str


@dataclass(frozen=True)
class CoinPrice:
    coin_symbol: str
    opening_price: int
    trade_price: int
    high_price: int
    low_price: int


@dataclass(frozen=True)
class CoinMarketData:
    market: str
    time: int
    data: CoinPrice
