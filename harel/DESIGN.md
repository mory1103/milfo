# harel デザイン規約 — 真昼の青空・ライトグラスモーフィズム

対象: `harel/index.html` + `harel/style.css`
方針: **CSSのみで再テーマ化**する。HTML構造・JSロジックは原則変更しない
（例外は「4. HTMLに許される変更」に列挙したもののみ）。

---

## 1. デザインコンセプト

- **真昼の澄んだ青空**を背景に、白いすりガラスのカードが浮かぶ**ライトテーマ**。
- グラデーションの終端に**ごく薄い黄色（陽光の色）**を混ぜて、画面全体に
  明るさと爽やかさを出す。黄色は「差し色」ではなく「光」として扱い、
  彩度・存在感を上げすぎない。
- harel は「もやもやを可視化する」内省アプリ。まぶしすぎる純白や
  ビビッドな原色は避け、晴れた日の屋外のような開放感を目指す。
- ガラス効果は背景に変化があって初めて見える。背景には**グラデーション＋
  ぼかした光のブロブ（装飾円）**を必ず敷く。

## 2. カラートークン（:root で一元管理）

既存の `:root` 変数を以下に**置き換える**。変数名は既存CSSの参照箇所を
壊さないよう、既存名を維持しつつ値を差し替える（不足分は追加）。

```css
:root{
  /* 背景グラデーション（真昼の空 → 薄い水色 → 陽光の淡い黄） */
  --bg1:#4a9de0;
  --bg2:#8fc8ef;
  --bg3:#fdf6dc;   /* ごく薄い黄色。明るさを担う「光」 */

  /* ガラス（ライトテーマ：白ガラス） */
  --glass-bg:rgba(255,255,255,.35);
  --glass-bg-strong:rgba(255,255,255,.50);   /* hover・強調面 */
  --glass-border:rgba(255,255,255,.65);
  --glass-shadow:0 8px 32px rgba(30,80,130,.18);
  --blur:16px;

  /* 既存変数の再定義 */
  --card:var(--glass-bg);
  --ink:#173a5c;                 /* 本文（濃紺。白文字は使わない） */
  --muted:rgba(23,58,92,.60);    /* 補助テキスト（半透明の濃紺） */
  --accent:#0ea5e9;              /* スカイブルー（メーター・チェック等） */
  --accent-deep:#0284c7;         /* グラデーション下端・ボタン背景の濃い側 */
  --accent-soft:rgba(14,165,233,.14); /* 選択面・タグ背景 */
  --line:rgba(23,58,92,.18);     /* 罫線・入力枠（半透明の濃紺） */
  --radius:20px;
  --maxw:560px;
}
```

**禁止**: 変数を経由しない色の直書きを新たに増やさない。旧ダーク版の配色
（濃紺背景 `#0b1a33` `#1b2a4a` `#2f4d80`、白文字 `#eef4fb` `#bae6fd`、
半透明白の `--muted` 等）を残さない。**ライトテーマなので文字は濃紺、
面は白系半透明**が原則。削除ボタンの赤は `#b04a4a`（明背景で読める深い赤）。

## 3. ガラス面の標準レシピ

`.card`・`.acc-toggle`・footer 以外に新しいガラス面を作るときも
必ずこのレシピに従う。

```css
background:var(--glass-bg);
border:1px solid var(--glass-border);
border-radius:var(--radius);
backdrop-filter:blur(var(--blur)) saturate(1.4);
-webkit-backdrop-filter:blur(var(--blur)) saturate(1.4);
box-shadow:var(--glass-shadow), inset 0 1px 0 rgba(255,255,255,.55);
```

- `inset 0 1px 0` の内側ハイライトが「ガラスの縁が光る」表現。省略しない。
  ライトテーマでは `.55` に強める（旧 `.12` はダーク用）。
- **フォールバック必須**:

```css
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
  .card,.acc-toggle{background:rgba(240,248,255,.92)}
}
```

## 4. HTMLに許される変更（これ以外は不可）

1. `<body>` 直下に装飾用の背景ブロブを追加する（**追加済み**）:
   `<div class="bg-decor" aria-hidden="true"><span></span><span></span><span></span></div>`
2. `<meta name="theme-color" content="#4a9de0">` を `<head>` に（**追加済み・値を更新**）。

ブロブは `position:fixed`・`border-radius:50%`・`filter:blur(80px)` 程度・
`pointer-events:none`・`z-index:-1`。色は**白い雲・陽光・淡い空色**の3種:
- `rgba(255,255,255,.50)`（雲）
- `rgba(255,249,196,.45)`（陽光のごく薄い黄。コンセプトの要）
- `rgba(125,211,252,.35)`（淡い空色）

サイズ 300〜480px を画面の左上・右中・左下あたりに散らす。
陽光ブロブは画面上部（太陽の方向）に置くとよい。

## 5. コンポーネント別ルール

| 部位 | ルール |
|---|---|
| body 背景 | `linear-gradient(160deg,var(--bg1),var(--bg2) 55%,var(--bg3))` を維持（色だけ差し替え）。`color-scheme:light` に変更 |
| `.card` | ガラスレシピ適用（インセットは `.55`） |
| header h1/p | 文字 `--ink`／`--muted`（濃紺。白文字禁止） |
| 入力欄（textarea/input） | `rgba(255,255,255,.55)` 面＋`--line` 枠＋`--ink` 文字。`::placeholder` は `--muted` |
| フォーカス | `outline:2px solid var(--accent-deep)`＋`outline-offset:2px`（ライト背景では deep の方が視認しやすい） |
| 選択肢 `.opt` | 通常時 `rgba(255,255,255,.30)`。checked 時 `--accent-soft` 面＋`--accent` 枠。`accent-color:var(--accent)` |
| `.btn-primary` | `linear-gradient(135deg,var(--accent-bright),var(--accent))`＋文字 `#082f49`（濃紺。白文字はスカイブルー上でコントラスト不足）。hover で明度up＋`translateY(-1px)` |
| `.btn-ghost` | 透明面＋`1px solid rgba(2,132,199,.35)` 枠＋文字 `var(--accent-deep)` |
| メーター | track は `rgba(255,255,255,.50)`、fill は `linear-gradient(90deg,var(--accent),var(--accent-deep))` |
| `.bar`（集計棒） | track `rgba(255,255,255,.45)`、fill はメーターと同じグラデーション |
| `.tag` | `--accent-soft` 面＋文字 `#075985`＋`1px solid rgba(14,165,233,.35)` |
| `.acc-toggle` | ガラスレシピ適用。文字 `--ink` |
| `#splash` | 背景グラデーションは body と同じトークン。**ロゴ・コピーとも `--ink`**（明背景に白文字は読めない） |
| footer | `background:rgba(255,255,255,.55)`＋`backdrop-filter:blur(12px)`＋`border-top:1px solid rgba(23,58,92,.10)`＋文字 `--muted` |
| 削除ボタン | 文字色 `#b04a4a` |
| アコーディオン閉時 | `.acc-body:not(.open) .acc-inner` を `visibility:hidden`（`transition:visibility 0s linear .35s` で閉じアニメ後に隠す）。旧デザインから存在した「閉じても padding 分のガラス板が残る」問題への対処 |

## 6. アクセシビリティ・品質基準

- 本文 `--ink`（#173a5c）は最も明るい面（白ガラス・淡黄 #fdf6dc）上でも
  コントラスト比 4.5:1 以上を確保する。
- `--muted` は補助テキスト専用。本文・ボタンラベルに使わない。
- `prefers-reduced-motion: reduce` でアニメーション（fade、メーター transition、
  hover の translateY）を無効化する media query を維持する。
- 既存のクラス名・ID・DOM構造・JSは変更しない（display切替やクラス付替えに
  依存しているため）。

## 8. 追加調整（2026-07-11 実装分）

以下は初回のライトテーマ実装後に加えた調整。セクション5の表を上書きする。

| 項目 | ルール |
|---|---|
| フォント | `"Zen Kaku Gothic New"` を第一候補に追加（Google Fonts。`index.html`の`<head>`でpreconnect＋読み込み）。フォールバックは既存のHiragino/Yu Gothic系を維持 |
| `.btn-primary` 文字色 | 白（`#fff`）＋`text-shadow:0 1px 2px rgba(2,49,74,.35)`で可読性確保。背景グラデーションは白文字とのコントラストを保つため`var(--accent)→var(--accent-deep)`寄りの中〜濃いブルーに調整（旧`accent-bright`起点の明るいグラデーションからの変更）。`.btn-ghost`は透明背景のため文字色は`var(--accent-deep)`のまま据え置き（白だと視認不可のため対象外） |
| `.opt`（選択肢チップ） | 枠線は維持しつつ`transition:background-color .4s ease, border-color .4s ease`を追加し、選択時の色変化を「ふわっと」させる |
| ラジオ／チェックボックス本体 | 縁取り（枠線）を撤去。`appearance:none`でネイティブ描画を止め、円/角丸四角のプレーンな面のみに。未選択時は半透明白、選択時は`background-color`が`var(--accent)`へ`.4s ease`でアニメーションしながら塗りつぶされ、`box-shadow`のソフトなグロー（`0 0 0 5px var(--accent-soft)`）が同時に広がる。チェックマークや内側ドットは付けず「面全体の色変化」のみで選択状態を表現 |
| 入力欄（textarea/input） | 枠線を撤去。代わりに`box-shadow:inset 0 1px 3px rgba(23,58,92,.10)`で控えめな沈み込みを表現し、ガラス面との一体感を保つ |
| ステップ遷移（次へ／戻る） | `fade`アニメーションを`.35s ease`から`.6s cubic-bezier(.19,1,.22,1)`に変更。`translateY`に加え`scale(.97→1)`と`filter:blur(8px→0)`を追加し、「すりガラスの向こうからピントが合う」ような、よりガラスらしい柔らかい遷移にする |
| 「これまでの記録」上下の余白 | `#accToggleList`に`margin-top:32px`を追加（ウィザードカードとの間を広げる）。`.acc-list`の`margin-bottom`を`18px→6px`に縮小（次の「体の反応の傾向」との間を詰める） |
| 共有リンク | footer内、コピーライト表示の上に`.footer-share`を追加。X／LINEへの共有ボタン（milfo本体 `index.html` の実装パターンを踏襲：`https://twitter.com/intent/tweet?...`／`https://social-plugins.line.me/lineit/share?url=...`）。**harelの本番URLが未確定のため、共有URLは`location.href`をJSで動的に埋め込む**（プレースホルダードメインは使わない）。デプロイ先が決まったら固定URLへの差し替えを検討 |
| footer の高さ | 共有ボタン行が増えた分、`body`の`padding-bottom`を`64px→120px`に拡大し、固定フッターが本文の最後のアコーディオンと重ならないようにする |

## 7. 検証チェックリスト（実装後に必ず確認）

- [ ] `style.css` 内に旧配色が残っていない。ダーク青版
  （`#0b1a33` `#1b2a4a` `#2f4d80` `#eef4fb` `#bae6fd` `#06203a` `#f8a5a5`
  `rgba(238,244,251` `rgba(11,26,51` `rgba(255,255,255,.16)` `rgba(255,255,255,.22)`）
  および夕焼け版・グリーン版の色が無いこと
- [ ] 文字色に白系（`#fff` 含む）を使っている箇所が無い（全て `--ink`/`--muted`/濃色）
- [ ] ガラス面すべてに `-webkit-backdrop-filter` 併記
- [ ] `@supports not` フォールバックがあり、ライト用の値になっている
- [ ] `color-scheme:light` に変更されている（date picker が明色）
- [ ] HTML の変更が「4.」の2点のみ（theme-color は `#4a9de0`）
- [ ] JSに変更がない
