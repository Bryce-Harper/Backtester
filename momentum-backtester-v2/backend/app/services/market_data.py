"""Market data pipeline: download, normalize, and cache OHLCV price data.

Data flows through three stages:

1. Download — ``_download_yfinance`` fetches raw bars from Yahoo Finance.
   Any callable with the same signature can be swapped in (other providers,
   test fakes) via the ``downloader`` argument of ``get_price_history``.
2. Normalize — raw frames are flattened to lowercase ``open/high/low/
   close/volume`` columns with a plain ``date`` column, NaN rows dropped.
3. Cache — normalized frames are stored as CSV under ``backend/data/cache``
   keyed by symbol, interval, and date range, so repeated queries never
   re-hit the provider.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Callable, Protocol

import pandas as pd

CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "cache"

VALID_INTERVALS = ("1d", "1wk", "1mo")

_COLUMNS = ["open", "high", "low", "close", "volume"]

_SYMBOL_RE = re.compile(r"^[A-Z0-9.\-^=]{1,20}$")


class MarketDataError(Exception):
    """Base error for the market data pipeline."""


class InvalidSymbolError(MarketDataError):
    """The requested symbol is malformed."""


class SymbolNotFoundError(MarketDataError):
    """The provider returned no data for the requested symbol/range."""


class ProviderError(MarketDataError):
    """The upstream data provider could not be reached or errored."""


Downloader = Callable[[str, date, date, str], pd.DataFrame]


def _download_yfinance(symbol: str, start: date, end: date, interval: str) -> pd.DataFrame:
    import yfinance as yf

    try:
        return yf.Ticker(symbol).history(
            start=start.isoformat(),
            end=end.isoformat(),
            interval=interval,
            auto_adjust=True,
            raise_errors=True,
        )
    except Exception as exc:
        # "No data found" style errors mean an unknown/delisted symbol —
        # return empty so the caller raises SymbolNotFoundError. Anything
        # else (network, rate limit, parse) is a provider failure.
        name = type(exc).__name__
        if name.startswith(("YFPricesMissing", "YFTickerMissing", "YFInvalidPeriod")):
            return pd.DataFrame()
        raise ProviderError(f"failed to download {symbol!r}: {exc}") from exc


def _normalize(raw: pd.DataFrame) -> pd.DataFrame:
    """Flatten a raw provider frame to date/open/high/low/close/volume."""
    if raw is None or raw.empty:
        return pd.DataFrame(columns=["date", *_COLUMNS])

    df = raw.copy()
    # yfinance returns MultiIndex columns like ('Close', 'AAPL') even for a
    # single ticker; keep only the field level.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in _COLUMNS if c not in df.columns]
    if missing:
        raise ProviderError(f"provider frame missing columns: {missing}")

    df = df[_COLUMNS]
    df.index.name = "date"
    df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.dropna(subset=["close"])
    df["volume"] = df["volume"].fillna(0).astype("int64")
    return df.sort_values("date").reset_index(drop=True)


def _cache_path(symbol: str, start: date, end: date, interval: str) -> Path:
    return CACHE_DIR / f"{symbol}_{interval}_{start.isoformat()}_{end.isoformat()}.csv"


def get_price_history(
    symbol: str,
    start: date,
    end: date,
    interval: str = "1d",
    downloader: Downloader | None = None,
) -> pd.DataFrame:
    """Return normalized OHLCV bars for a symbol, using the disk cache.

    Raises InvalidSymbolError, SymbolNotFoundError, or ProviderError.
    """
    symbol = symbol.strip().upper()
    if not _SYMBOL_RE.match(symbol):
        raise InvalidSymbolError(f"invalid symbol: {symbol!r}")
    if interval not in VALID_INTERVALS:
        raise MarketDataError(f"invalid interval: {interval!r}")

    path = _cache_path(symbol, start, end, interval)
    if path.exists():
        cached = pd.read_csv(path)
        cached["date"] = pd.to_datetime(cached["date"]).dt.date
        return cached

    raw = (downloader or _download_yfinance)(symbol, start, end, interval)
    df = _normalize(raw)
    if df.empty:
        raise SymbolNotFoundError(f"no data for {symbol!r} between {start} and {end}")

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df
