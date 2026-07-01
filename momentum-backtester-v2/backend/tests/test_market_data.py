from datetime import date

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import market_data

START = date(2026, 1, 5)
END = date(2026, 1, 9)


def yfinance_style_frame() -> pd.DataFrame:
    """Mimic yfinance output: MultiIndex columns, DatetimeIndex, NaN row."""
    idx = pd.DatetimeIndex(
        ["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"], name="Date"
    )
    cols = pd.MultiIndex.from_product(
        [["Open", "High", "Low", "Close", "Volume"], ["TEST"]]
    )
    df = pd.DataFrame(
        [
            [10.0, 11.0, 9.5, 10.5, 1000],
            [10.5, 12.0, 10.0, 11.5, 2000],
            [None, None, None, None, None],  # holiday gap -> dropped
            [11.5, 12.5, 11.0, 12.0, 1500],
        ],
        index=idx,
        columns=cols,
    )
    return df


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(market_data, "CACHE_DIR", tmp_path / "cache")


def test_normalize_flattens_and_drops_nan_rows():
    df = market_data._normalize(yfinance_style_frame())
    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert len(df) == 3  # NaN row dropped
    assert df["date"].tolist() == [
        date(2026, 1, 5),
        date(2026, 1, 6),
        date(2026, 1, 8),
    ]
    assert df["volume"].dtype == "int64"


def test_get_price_history_caches_downloads():
    calls = []

    def fake_downloader(symbol, start, end, interval):
        calls.append(symbol)
        return yfinance_style_frame()

    first = market_data.get_price_history(
        "test", START, END, "1d", downloader=fake_downloader
    )
    second = market_data.get_price_history(
        "test", START, END, "1d", downloader=fake_downloader
    )
    assert calls == ["TEST"]  # second call served from cache
    pd.testing.assert_frame_equal(first, second)


def test_empty_result_raises_symbol_not_found():
    def empty_downloader(symbol, start, end, interval):
        return pd.DataFrame()

    with pytest.raises(market_data.SymbolNotFoundError):
        market_data.get_price_history(
            "NOPE", START, END, "1d", downloader=empty_downloader
        )


def test_invalid_symbol_rejected_before_download():
    with pytest.raises(market_data.InvalidSymbolError):
        market_data.get_price_history(
            "bad symbol!", START, END, "1d", downloader=None
        )


def test_prices_endpoint_returns_bars(monkeypatch):
    monkeypatch.setattr(
        market_data, "_download_yfinance", lambda *a: yfinance_style_frame()
    )
    client = TestClient(app)
    resp = client.get(f"/api/prices/test?start={START}&end={END}&interval=1d")
    assert resp.status_code == 200
    body = resp.json()
    assert body["symbol"] == "TEST"
    assert body["count"] == 3
    assert body["bars"][0] == {
        "date": "2026-01-05",
        "open": 10.0,
        "high": 11.0,
        "low": 9.5,
        "close": 10.5,
        "volume": 1000,
    }


def test_prices_endpoint_404_for_unknown_symbol(monkeypatch):
    monkeypatch.setattr(
        market_data, "_download_yfinance", lambda *a: pd.DataFrame()
    )
    client = TestClient(app)
    resp = client.get(f"/api/prices/NOPE?start={START}&end={END}")
    assert resp.status_code == 404


def test_prices_endpoint_400_for_backwards_range():
    client = TestClient(app)
    resp = client.get(f"/api/prices/TEST?start={END}&end={START}")
    assert resp.status_code == 400
