from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class CoinSymbol:
    coin_symbol: str


@dataclass(frozen=True)
class CoinPrice:
    opening_price: float
    prev_closing_price: float
    high_price: float
    low_price: float
    volumne_24: float


@dataclass(frozen=True)
class CoinMarketData:
    market: str
    time: int
    coin_symbol: str
    data: CoinPrice
