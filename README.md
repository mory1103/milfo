# stasis — セットアップガイド

## ファイル構成

```
stasis/
├── app.py              ← バックエンド（FastAPI + yfinance）
├── portfolio-sim.html  ← フロントエンド
└── README.md
```

---

## 1. バックエンドのセットアップ

### ライブラリをインストール

```bash
pip install fastapi uvicorn yfinance
```

### 起動

```bash
uvicorn app:app --reload --port 8000
```

ブラウザで http://localhost:8000/docs を開くと  
Swagger UI（API の動作確認画面）が確認できます。

---

## 2. フロントエンドの接続切り替え

`portfolio-sim.html` の中の `API_BASE` を変更するだけです。

```js
// portfolio-sim.html 内
const API_BASE = 'http://localhost:8000';  // ← バックエンド起動後にこれを有効にする
// const API_BASE = null;                  // null = デモデータモード
```

---

## 3. API エンドポイント一覧

### 銘柄情報取得
```
GET /api/stock?ticker=7203&market=JP
GET /api/stock?ticker=AAPL&market=US
```

レスポンス例:
```json
{
  "id": "JP_7203",
  "ticker": "7203",
  "market": "JP",
  "name": "Toyota Motor Corp",
  "price": 3712.0,
  "change": 1.24,
  "per": 9.8,
  "pbr": 1.1,
  "divYield": 2.6,
  "div": 72,
  "growth": 55,
  "value": 80,
  "stable": 85,
  "momentum": 60
}
```

### 銘柄検索（サジェスト用）
```
GET /api/search?q=トヨタ
GET /api/search?q=Apple
```

レスポンス例:
```json
[
  { "ticker": "7203.T", "name": "Toyota Motor Corp", "exchange": "JPX", "type": "EQUITY" }
]
```

### USD/JPY 為替レート
```
GET /api/rate
```

レスポンス例:
```json
{ "rate": 155.23, "cached": false }
```

---

## 4. 日本株のティッカー形式

yfinance では東証銘柄に `.T` を付ける必要があります。  
バックエンド側で自動付与するので、フロントからは `7203` のまま送ればOKです。

```
7203  →（バックエンドで）→  7203.T
```

---

## 5. よくあるエラー

| エラー | 原因 | 対処 |
|--------|------|------|
| `yfinance error` | Yahoo Finance 側の一時障害 | しばらく待って再試行 |
| `404 銘柄が見つかりません` | ティッカーが間違っている | 証券コードを確認 |
| `CORS error`（ブラウザ） | バックエンドが起動していない | `uvicorn` を起動する |
| データが空 / `null` | 日本株の一部フィールド未対応 | フォールバック値（50）を使用 |

---

## 6. Claude Code での修正のヒント

```bash
# プロジェクトフォルダで起動
cd stasis
claude

# 例）こんな指示が通ります
> /api/stock のレスポンスに sector（セクター）フィールドを追加して
> 成長スコアの計算ロジックを earningsGrowth だけで計算するように変更して
> /api/search の結果を日本株だけに絞るフィルターを追加して
```
