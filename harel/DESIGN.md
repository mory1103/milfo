# harel デザインシステム — グラスモーフィズム版

harel（もやもやを、可視化する）のUIをグラスモーフィズムで統一するためのルール。
実装者はこのドキュメントに**厳密に従うこと**。ここに書かれていない装飾を勝手に追加しない。

## 0. コンセプト

- 世界観は現行の「夜明け前 → 朝焼け」のグラデーションを**維持**する。
  グラスモーフィズムはこの背景の上に「すりガラスのカード」を浮かべる表現。
- 感情記録アプリなので、トーンは**静かで柔らかく**。彩度の高い色・強い発光・
  派手なアニメーションは禁止。

## 1. デザイントークン（:root 変数）

既存の `:root` を以下に**置き換える**。変数名は既存のものを維持しつつ拡張する。

```css
:root{
  /* 背景グラデーション（現行を維持） */
  --bg1:#1b2a4a;   /* 夜明け前の濃い青 */
  --bg2:#7c6f9e;   /* 紫がかった移行 */
  --bg3:#f6c9a8;   /* 朝焼けのオレンジ */

  /* ガラス面 */
  --glass-bg:rgba(255,255,255,.10);        /* 基本ガラス */
  --glass-bg-strong:rgba(255,255,255,.16); /* ホバー・強調時 */
  --glass-border:rgba(255,255,255,.22);    /* 1px 枠線 */
  --glass-highlight:rgba(255,255,255,.35); /* 上辺ハイライト */
  --glass-shadow:0 8px 32px rgba(15,20,45,.30);
  --glass-blur:16px;

  /* テキスト（すべて白系。暗色テキストは使わない） */
  --ink:#ffffff;
  --muted:rgba(255,255,255,.70);   /* 補助テキスト */
  --muted2:rgba(255,255,255,.50);  /* プレースホルダ等さらに弱く */

  /* アクセント */
  --accent:#8fb4e8;                 /* リンク・チェック・チャート等（明るい青） */
  --accent-strong:#5b84c4;          /* 主ボタンのグラデ下端 */
  --danger:#f2a6a6;                 /* 削除等（ガラス上で読める明るい赤） */

  --radius:18px;
  --radius-sm:12px;
  --maxw:560px;
}
```

**注意**: 旧 `--muted:#6b7180`・`--accent-soft`・`--line` は廃止。
`--accent-soft` / `--line` を参照している箇所はすべてガラス系変数に置き換える。

## 2. ガラス面の標準レシピ

ガラス面（カード・アコーディオンボタン・入力欄・選択肢）は必ずこの組み合わせで作る：

```css
background:var(--glass-bg);
backdrop-filter:blur(var(--glass-blur)) saturate(1.4);
-webkit-backdrop-filter:blur(var(--glass-blur)) saturate(1.4);
border:1px solid var(--glass-border);
border-radius:var(--radius);      /* 小要素は --radius-sm */
box-shadow:var(--glass-shadow),
           inset 0 1px 0 var(--glass-highlight);  /* 上辺の光 */
```

ルール：
- `-webkit-backdrop-filter` を**必ず併記**（iOS Safari対応）。
- **フォールバック必須**：`@supports not (backdrop-filter: blur(1px))` で
  `background:rgba(35,45,80,.85)` に差し替える（ガラス無しでも文字が読めること）。
- `backdrop-filter` はコストが高い。**ネストしない**（カードの中の入力欄・選択肢は
  `backdrop-filter` を付けず、`background:rgba(255,255,255,.08)` + 枠線のみの
  「疑似ガラス」にする）。1画面あたり backdrop-filter を持つ要素は
  トップレベルのガラス面（card / acc-toggle / footer / splash後のUI）だけに限定。

## 3. 背景の装飾（グラスを効かせるための下地）

すりガラスは背後に色の変化がないと視認できない。body 直下に装飾用の
ぼかし円（オーブ）を2〜3個追加する：

- `body::before` / `body::after`（または `.bg-orb` div）で実装。
- `position:fixed`、`border-radius:50%`、`filter:blur(80px)`、
  `pointer-events:none`、`z-index:-1`。
- 色は `--bg3`（オレンジ系）と `--accent` 系の半透明（alpha 0.25〜0.35）。
- **アニメーションさせない**（静的配置。パフォーマンスと落ち着きのため）。
- 配置例：右上に大きめ1個（オレンジ）、左下に1個（青紫）。

## 4. コンポーネント別仕様

### 4.1 カード（.card）
- 標準レシピをそのまま適用。padding は現行値（22px 20px）を維持。

### 4.2 入力欄（textarea / input[type=text] / input[type=date]）
- **現行の `background:#fff` + 白文字は白地に白文字で読めないバグ。必ず直す。**
- 疑似ガラス：`background:rgba(255,255,255,.08)`、`border:1px solid var(--glass-border)`、
  `border-radius:var(--radius-sm)`、`color:var(--ink)`。
- placeholder は `color:var(--muted2)`。
- focus 時：`border-color:var(--accent)` + `box-shadow:0 0 0 3px rgba(143,180,232,.25)`。
  `outline` の2px実線は廃止（ガラスと喧嘩するため）。
- `input[type=date]` は `color-scheme:dark` を指定（ネイティブUIを暗色に）。

### 4.3 選択肢（.opt）
- 疑似ガラス（backdrop-filterなし）。
- checked 時：`background:rgba(143,180,232,.20)` + `border-color:var(--accent)`。
  文字は白のまま（旧 `--accent-soft` 背景 + アクセント文字は使わない）。
- `accent-color:var(--accent)` を維持。

### 4.4 ボタン
- `.btn-primary`：唯一の「非ガラス」要素。
  `background:linear-gradient(180deg,var(--accent),var(--accent-strong))`、
  白文字、`border-radius:var(--radius-sm)`、
  `box-shadow:0 4px 16px rgba(91,132,196,.40)`。
  hover で `filter:brightness(1.08)`。
- `.btn-ghost`：疑似ガラス + 白文字（`color:var(--ink)`。旧アクセント文字は
  背景上でコントラスト不足のため白へ）。hover で `background:var(--glass-bg-strong)`。

### 4.5 メーター（.meter）
- track：`background:rgba(255,255,255,.15)`。
- fill：`linear-gradient(90deg,var(--accent),var(--bg3))`（夜明けの比喩）。
- label：`color:var(--muted)`。

### 4.6 まとめ（.summary）・タグ（.tag）
- dt は `color:var(--muted)`。
- `.tag`：疑似ガラスのピル。`background:rgba(143,180,232,.20)`、
  `border:1px solid rgba(143,180,232,.35)`、`color:#dce9fb`。

### 4.7 記録一覧（.entry）・チャート（.bar-row）
- 区切り線：`border-bottom:1px solid rgba(255,255,255,.12)`。
- 削除ボタン：`color:var(--danger)`。
- `.bar`：track は `rgba(255,255,255,.15)`、fill はメーターと同じグラデ。
- `.name` / `.n` / `.meta` / `.empty`：`color:var(--muted)`。

### 4.8 アコーディオン（.acc-toggle / .acc-body）
- `.acc-toggle` は標準ガラスレシピ。開閉ロジック・grid アニメーションは変更しない。
- chevron の色は `var(--accent)` を維持。

### 4.9 フッター（footer）
- `background:rgba(20,28,55,.55)` + `backdrop-filter:blur(12px)`（+ -webkit- / フォールバック）。
- `border-top:1px solid rgba(255,255,255,.10)`。

### 4.10 スプラッシュ（#splash）
- 背景グラデーションと表示ロジックは**変更しない**。フェードの時間・JSも触らない。

## 5. モーション・アクセシビリティ

- アニメーションは既存のもの（step の fade、メーター遷移、アコーディオン、
  スプラッシュ）だけ。新規追加禁止。ガラス面に transform ホバー等を付けない。
- `@media (prefers-reduced-motion: reduce)` を追加し、transition / animation を
  ほぼ無効化（`transition-duration:.01ms` 等）する。
- コントラスト：本文=白 / 補助=`--muted`（alpha .70）を下回る文字色を本文系に
  使わない。alpha .50（--muted2）はプレースホルダと著作権表記のみ。

## 6. 変更してはいけないもの

- **JavaScript（index.html 内の `<script>`）は一切変更しない。**
- HTML 構造の変更は「背景オーブ用の要素追加」が必要な場合のみ最小限に
  （CSS疑似要素で実現できるなら HTML は無変更が望ましい）。
- クラス名・ID は変更しない（JSが参照しているため）。
- 文言・ステップ構成・localStorage キーは変更しない。
