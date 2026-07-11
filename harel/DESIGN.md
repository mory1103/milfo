# harel デザイン規約 — ブルーベース・グラスモーフィズム

対象: `harel/index.html` + `harel/style.css`
方針: **CSSのみで再テーマ化**する。HTML構造・JSロジックは原則変更しない
（例外は「4. HTMLに許される変更」に列挙したもののみ）。

---

## 1. デザインコンセプト

- 夜明け前の深い青を背景に、すりガラス（グラスモーフィズム）のカードが浮かぶ。
- harel は「もやもやを可視化する」内省アプリ。落ち着き・安心感を最優先し、
  彩度の高い派手な色は避ける。青は静けさ・思索の色として基調に据える。
- 背景は**青系グラデーション**（夕焼けオレンジは使わない）。かつて harel が
  持っていた `#1b2a4a`（夜明け前の濃い青）の記憶を残しつつ、全体を青で統一する。
- ガラス効果は背景に変化があって初めて見える。背景には**グラデーション＋
  ぼかした光のブロブ（装飾円）**を必ず敷く。

## 2. カラートークン（:root で一元管理）

既存の `:root` 変数を以下に**置き換える**。変数名は既存CSSの参照箇所を
壊さないよう、既存名を維持しつつ値を差し替える（不足分は追加）。

```css
:root{
  /* 背景グラデーション（夜明け前の濃紺 → 藍 → 青） */
  --bg1:#0b1a33;
  --bg2:#1b2a4a;   /* 旧 harel の「夜明け前の濃い青」を継承 */
  --bg3:#2f4d80;

  /* ガラス */
  --glass-bg:rgba(255,255,255,.10);
  --glass-bg-strong:rgba(255,255,255,.16);   /* hover・強調面 */
  --glass-border:rgba(255,255,255,.22);
  --glass-shadow:0 8px 32px rgba(4,12,28,.35);
  --blur:16px;

  /* 既存変数の再定義 */
  --card:var(--glass-bg);
  --ink:#eef4fb;                 /* 本文（ほぼ白、青がかり） */
  --muted:rgba(238,244,251,.62); /* 補助テキスト（半透明白） */
  --accent:#38bdf8;              /* スカイブルー（ボタン・メーター） */
  --accent-deep:#0284c7;         /* ボタングラデーションの下端 */
  --accent-soft:rgba(56,189,248,.16); /* 選択面・タグ背景 */
  --line:rgba(255,255,255,.16);  /* 罫線・入力枠 */
  --radius:20px;
  --maxw:560px;
}
```

**禁止**: 変数を経由しない色の直書きを新たに増やさない。旧配色（夕焼けの
`#f6c9a8` や中間版のエメラルド `#34d399`/`#059669`/`#a7f3d0` 等）を残さない。
削除ボタンの赤だけは `#f8a5a5`（暗背景で読める淡い赤）を使ってよい。

## 3. ガラス面の標準レシピ

`.card`・`.acc-toggle`・`#splash` 以外に新しいガラス面を作るときも
必ずこのレシピに従う。

```css
background:var(--glass-bg);
border:1px solid var(--glass-border);
border-radius:var(--radius);
backdrop-filter:blur(var(--blur)) saturate(1.4);
-webkit-backdrop-filter:blur(var(--blur)) saturate(1.4);
box-shadow:var(--glass-shadow), inset 0 1px 0 rgba(255,255,255,.12);
```

- `inset 0 1px 0` の内側ハイライトが「ガラスの縁が光る」表現。省略しない。
- **フォールバック必須**:

```css
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
  .card,.acc-toggle{background:rgba(11,26,51,.88)}
}
```

## 4. HTMLに許される変更（これ以外は不可）

1. `<body>` 直下に装飾用の背景ブロブを追加する:
   `<div class="bg-decor" aria-hidden="true"><span></span><span></span><span></span></div>`
2. `<meta name="theme-color" content="#0b2b21">` を `<head>` に追加。

ブロブは `position:fixed`・`border-radius:50%`・`filter:blur(80px)` 程度・
`pointer-events:none`・`z-index:-1`。色はブルー／シアン系
（例 `rgba(56,189,248,.22)`、`rgba(125,211,252,.16)`、`rgba(14,165,233,.20)`）。
サイズ 300〜480px を画面の左上・右中・左下あたりに散らす。

## 5. コンポーネント別ルール

| 部位 | ルール |
|---|---|
| body 背景 | `linear-gradient(160deg,var(--bg1),var(--bg2) 55%,var(--bg3))` を維持（色だけ緑に） |
| `.card` | ガラスレシピ適用。既存の `blur(4px)` は `var(--blur)` に強化 |
| 入力欄（textarea/input） | 白背景をやめ `rgba(255,255,255,.08)`＋`--line` 枠＋`--ink` 文字。`::placeholder` は `--muted`。`color-scheme:dark` を body に指定し date picker も暗色化 |
| フォーカス | `outline:2px solid var(--accent)`＋`outline-offset:2px` に統一（`focus-visible` 推奨） |
| 選択肢 `.opt` | 通常時 `rgba(255,255,255,.06)`。checked 時 `--accent-soft` 面＋`--accent` 枠。`accent-color:var(--accent)` |
| `.btn-primary` | `linear-gradient(135deg,var(--accent),var(--accent-deep))`＋文字 `#06203a`（濃紺。白文字はスカイブルー上でコントラスト不足）。hover で明度up＋`translateY(-1px)` |
| `.btn-ghost` | 透明面＋`--glass-border` 枠＋文字 `#bae6fd` |
| メーター | track は `rgba(255,255,255,.15)`、fill は accent グラデーション |
| `.bar`（集計棒） | track `rgba(255,255,255,.12)`、fill は accent グラデーション |
| `.tag` | `--accent-soft` 面＋文字 `#bae6fd`＋`1px solid rgba(56,189,248,.35)` |
| `.acc-toggle` | ガラスレシピ適用（既存の box-shadow 直書きを置換） |
| `#splash` | 背景グラデーションを青に（body と同じトークン）。ロゴ文字はそのまま白 |
| footer | `background:rgba(11,26,51,.80)`＋`backdrop-filter:blur(12px)`（下端もガラスに） |
| 削除ボタン | 文字色 `#f8a5a5` |
| アコーディオン閉時 | `.acc-body:not(.open) .acc-inner` を `visibility:hidden`（`transition:visibility 0s linear .35s` で閉じアニメ後に隠す）。旧デザインから存在した「閉じても padding 分のガラス板が残る」問題への対処 |

## 6. アクセシビリティ・品質基準

- 本文 `--ink` は背景緑に対しコントラスト比 4.5:1 以上を確保（上記値で満たす）。
- `--muted` は補助テキスト専用。本文・ボタンラベルに使わない。
- `prefers-reduced-motion: reduce` でアニメーション（fade、メーター transition、
  hover の translateY）を無効化する media query を追加。
- 既存のクラス名・ID・DOM構造・JSは変更しない（display切替やクラス付替えに
  依存しているため）。

## 7. 検証チェックリスト（実装後に必ず確認）

- [ ] `style.css` 内に旧配色が残っていない。夕焼け系（`#7c6f9e` `#f6c9a8` `#4a6fa5` `#e8eef7` `#e3e6ee` `#6b7180`）および中間グリーン版（`#34d399` `#059669` `#0b2b21` `#14532d` `#2f6b4f` `#a7f3d0` `#06281c` `rgba(52,211,153` `rgba(110,231,183` `rgba(16,185,129`）が無いこと。※`#1b2a4a` は新 `--bg2` として意図的に継続使用
- [ ] ガラス面すべてに `-webkit-backdrop-filter` 併記
- [ ] `@supports not` フォールバックがある
- [ ] 入力欄・date picker が暗色で表示される（`color-scheme`）
- [ ] HTML の変更が「4.」の2点のみ
- [ ] JSに変更がない
