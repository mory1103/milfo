"""
milfo — バックエンド API
==============================
使用ライブラリ:
    pip install fastapi uvicorn yfinance

起動:
    uvicorn app:app --reload --port 8000

エンドポイント一覧:
    GET /api/stock?ticker=7203&market=JP   銘柄情報取得
    GET /api/search?q=Toyota&market=JP     銘柄検索（候補リスト）
    GET /api/rate                          USD/JPY 為替レート取得
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yfinance as yf
import sqlite3
import json
import time
import threading
from pathlib import Path
from typing import Optional

app = FastAPI(title="milfo API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── フロントエンド配信 ────────────────────────────────────────────────
@app.get("/")
def serve_index():
    return FileResponse(Path(__file__).resolve().parent / "index.html")

# ── キャッシュ設定 ────────────────────────────────────────────────────
STOCK_TTL = 6 * 3600   # 銘柄データ: 6時間
RATE_TTL  = 600        # 為替レート: 10分
DB_PATH   = Path(__file__).resolve().parent / "cache.db"

_db_lock = threading.Lock()


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key       TEXT PRIMARY KEY,
            payload   TEXT NOT NULL,
            cached_at REAL NOT NULL
        )
    """)
    con.commit()
    return con


def cache_get(key: str, ttl: float) -> Optional[dict]:
    """TTL 内のキャッシュを返す。期限切れ・未存在は None。"""
    with _db_lock:
        con = _db()
        row = con.execute(
            "SELECT payload, cached_at FROM cache WHERE key = ?", (key,)
        ).fetchone()
        con.close()
    if row and (time.time() - row[1]) < ttl:
        return json.loads(row[0])
    return None


def cache_get_stale(key: str) -> Optional[dict]:
    """期限に関わらずキャッシュを返す（フォールバック用）。"""
    with _db_lock:
        con = _db()
        row = con.execute(
            "SELECT payload FROM cache WHERE key = ?", (key,)
        ).fetchone()
        con.close()
    return json.loads(row[0]) if row else None


def cache_set(key: str, data: dict) -> None:
    with _db_lock:
        con = _db()
        con.execute(
            "INSERT OR REPLACE INTO cache (key, payload, cached_at) VALUES (?, ?, ?)",
            (key, json.dumps(data), time.time()),
        )
        con.commit()
        con.close()


# ── ティッカー整形 ────────────────────────────────────────────────────
def format_ticker(ticker: str, market: str) -> str:
    t = ticker.strip().upper()
    if market.upper() == "JP" and not t.endswith(".T"):
        t += ".T"
    return t


# ── スコア計算 ───────────────────────────────────────────────────────
def calc_scores(info: dict) -> dict:
    def clamp(v, lo=0, hi=100):
        return max(lo, min(hi, round(v)))

    dy       = info.get("dividendYield") or 0
    dividend = clamp(dy / 0.06 * 100)

    rg     = info.get("revenueGrowth") or info.get("earningsGrowth") or 0
    growth = clamp(rg / 0.30 * 100)

    pe        = info.get("trailingPE")  or 0
    pbr       = info.get("priceToBook") or 0
    per_score = clamp(100 - pe  * 2)  if pe  > 0 else 50
    pbr_score = clamp(100 - pbr * 15) if pbr > 0 else 50
    value     = clamp((per_score + pbr_score) / 2)

    beta   = info.get("beta") or 1.0
    stable = clamp(100 - beta * 50)

    hi52 = info.get("fiftyTwoWeekHigh") or 0
    lo52 = info.get("fiftyTwoWeekLow")  or 0
    cur  = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    momentum = clamp((cur - lo52) / (hi52 - lo52) * 100) if hi52 > lo52 and cur > 0 else 50

    return {"div": dividend, "growth": growth, "value": value, "stable": stable, "momentum": momentum}


# ── yfinance から銘柄データを取得してレスポンス形式に整形 ──────────────
def _fetch_from_yfinance(sym: str, ticker: str, market: str) -> dict:
    tk   = yf.Ticker(sym)
    info = tk.info
    if not info.get("symbol") and not info.get("shortName"):
        raise ValueError(f"銘柄が見つかりません: {sym}")
    cur        = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    prev       = info.get("previousClose") or cur
    change_pct = round((cur - prev) / prev * 100, 2) if prev else 0.0
    return {
        "id":       market.upper() + "_" + ticker.upper(),
        "ticker":   ticker.upper(),
        "market":   market.upper(),
        "name":     info.get("shortName") or info.get("longName") or sym,
        "price":    cur,
        "change":   change_pct,
        "per":      round(info.get("trailingPE")      or 0, 1),
        "pbr":      round(info.get("priceToBook")     or 0, 1),
        "divYield": round((info.get("dividendYield")  or 0) * 100, 2),
        **calc_scores(info),
    }


def get_stock_data(ticker: str, market: str) -> dict:
    """
    キャッシュ確認 → 新鮮なら返す → 古い/なければ yfinance 取得 → 保存して返す。
    yfinance 失敗時は古いキャッシュにフォールバック。キャッシュも無ければ例外を上げる。
    """
    sym       = format_ticker(ticker, market)
    cache_key = f"stock:{sym}"

    cached = cache_get(cache_key, STOCK_TTL)
    if cached:
        return cached

    try:
        data = _fetch_from_yfinance(sym, ticker, market)
        cache_set(cache_key, data)
        return data
    except Exception as e:
        stale = cache_get_stale(cache_key)
        if stale:
            return stale
        raise e


# ── /api/stock ────────────────────────────────────────────────────────
@app.get("/api/stock")
def get_stock(
    ticker: str = Query(...),
    market: str = Query("JP"),
):
    try:
        return get_stock_data(ticker, market)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"取得失敗: {e}")


# ── /api/search ───────────────────────────────────────────────────────
@app.get("/api/search")
def search_stock(
    q:      str = Query(...),
    market: str = Query("JP"),
):
    try:
        results = yf.Search(q, max_results=8).quotes
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"search error: {e}")

    return [
        {
            "ticker":   r.get("symbol", ""),
            "name":     r.get("shortname") or r.get("longname") or "",
            "exchange": r.get("exchange", ""),
            "type":     r.get("quoteType", ""),
        }
        for r in results
        if r.get("quoteType") in ("EQUITY", "ETF")
    ]


# ── /api/rate ─────────────────────────────────────────────────────────
@app.get("/api/rate")
def get_rate():
    cache_key = "rate:USDJPY"

    cached = cache_get(cache_key, RATE_TTL)
    if cached:
        return {"rate": cached["rate"], "cached": True}

    try:
        info = yf.Ticker("USDJPY=X").info
        rate = info.get("regularMarketPrice") or info.get("bid") or 150.0
        data = {"rate": round(rate, 2)}
        cache_set(cache_key, data)
        return {"rate": data["rate"], "cached": False}
    except Exception:
        stale = cache_get_stale(cache_key)
        rate  = stale["rate"] if stale else 150.0
        return {"rate": rate, "cached": True, "fallback": True}
