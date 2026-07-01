from datetime import date

from pydantic import BaseModel


class PriceBar(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class PriceHistory(BaseModel):
    symbol: str
    interval: str
    start: date
    end: date
    count: int
    bars: list[PriceBar]
