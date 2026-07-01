from datetime import date, timedelta
from typing import Literal

from fastapi import APIRouter, HTTPException

from app.models.market_data import PriceBar, PriceHistory
from app.services import market_data

router = APIRouter(tags=["market-data"])


@router.get("/prices/{symbol}", response_model=PriceHistory)
def read_price_history(
    symbol: str,
    start: date | None = None,
    end: date | None = None,
    interval: Literal["1d", "1wk", "1mo"] = "1d",
) -> PriceHistory:
    """Return OHLCV price history for a symbol.

    Defaults to the trailing year of daily bars when no dates are given.
    """
    end = end or date.today()
    start = start or end - timedelta(days=365)
    if start >= end:
        raise HTTPException(status_code=400, detail="start must be before end")

    try:
        df = market_data.get_price_history(symbol, start, end, interval)
    except market_data.InvalidSymbolError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except market_data.SymbolNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except market_data.ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    bars = [PriceBar(**row) for row in df.to_dict("records")]
    return PriceHistory(
        symbol=symbol.strip().upper(),
        interval=interval,
        start=start,
        end=end,
        count=len(bars),
        bars=bars,
    )
