from dataclasses import dataclass


@dataclass(frozen=True)
class CoinSymbol:
    coin_symbol: str
