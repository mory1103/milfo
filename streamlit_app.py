import streamlit as st
import yfinance as yf

st.set_page_config(page_title="milfo", layout="centered")
st.title("milfo")


# ── ティッカー整形 ────────────────────────────────────────────────────
def format_ticker(ticker: str, market: str) -> str:
    t = ticker.strip().upper()
    if market.upper() == "JP" and not t.endswith(".T"):
        t += ".T"
    return t


# ── ポテンシャルスコア計算 ────────────────────────────────────────────
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

    beta     = info.get("beta") or 1.0
    stable   = clamp(100 - beta * 50)

    hi52     = info.get("fiftyTwoWeekHigh") or 0
    lo52     = info.get("fiftyTwoWeekLow")  or 0
    cur      = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    momentum = clamp((cur - lo52) / (hi52 - lo52) * 100) if hi52 > lo52 and cur > 0 else 50

    return {
        "div":      dividend,
        "growth":   growth,
        "value":    value,
        "stable":   stable,
        "momentum": momentum,
    }


# ── 為替レート（10分キャッシュ、失敗時はフォールバック150円） ──────────
@st.cache_data(ttl=600)
def get_usdjpy_rate() -> float:
    try:
        info = yf.Ticker("USDJPY=X").info
        rate = info.get("regularMarketPrice") or info.get("bid") or 150.0
        return round(float(rate), 2)
    except Exception:
        return 150.0

st.sidebar.metric("USD/JPY", f"{get_usdjpy_rate():.2f}")


# ── 検索（候補リスト） ────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def search_tickers(q: str, market: str) -> list:
    try:
        results = yf.Search(q, max_results=8).quotes
    except Exception:
        return []
    return [
        {
            "ticker":   r.get("symbol", ""),
            "name":     r.get("shortname") or r.get("longname") or "",
            "exchange": r.get("exchange", ""),
        }
        for r in results
        if r.get("quoteType") in ("EQUITY", "ETF")
    ]


# ── 株価データ取得（6時間キャッシュ） ────────────────────────────────
@st.cache_data(ttl=21600)
def get_stock_data(ticker: str, market: str) -> dict:
    sym  = format_ticker(ticker, market)
    tk   = yf.Ticker(sym)
    info = tk.info
    if not info.get("symbol") and not info.get("shortName"):
        raise ValueError(f"銘柄が見つかりません: {sym}")

    cur        = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    prev       = info.get("previousClose") or cur
    change_pct = round((cur - prev) / prev * 100, 2) if prev else 0.0
    scores     = calc_scores(info)

    return {
        "name":           info.get("shortName") or info.get("longName") or sym,
        "price":          cur,
        "change":         change_pct,
        "per":            round(info.get("trailingPE")     or 0, 1),
        "pbr":            round(info.get("priceToBook")    or 0, 1),
        "dividend_yield": round((info.get("dividendYield") or 0) * 100, 2),
        **scores,
    }


# ── UI ───────────────────────────────────────────────────────────────
query  = st.text_input("企業名・ティッカーで検索（英語で入力：Toyota / Apple）")
market = st.selectbox("市場", ["JP", "US"])

if query:
    candidates = search_tickers(query, market)
    if candidates:
        labels   = [f"{c['name']}（{c['ticker']}）" for c in candidates]
        selected = st.selectbox("候補から選択", labels)
        ticker   = candidates[labels.index(selected)]["ticker"]

        try:
            data = get_stock_data(ticker, market)
        except ValueError as e:
            st.error(str(e))
            st.stop()

        st.subheader(data["name"])

        c1, c2, c3 = st.columns(3)
        c1.metric("株価",   data["price"],  f"{data['change']:+.2f}%")
        c2.metric("PER",    data["per"])
        c3.metric("PBR",    data["pbr"])
        st.metric("配当利回り", f"{data['dividend_yield']:.2f}%")

        st.divider()
        st.subheader("ポテンシャルスコア")
        score_labels = {
            "div":      "配当",
            "growth":   "成長",
            "value":    "割安",
            "stable":   "安定",
            "momentum": "勢い",
        }
        for key, label in score_labels.items():
            st.progress(data[key], text=f"{label}　{data[key]}")
    else:
        st.info("該当する候補が見つかりませんでした")
