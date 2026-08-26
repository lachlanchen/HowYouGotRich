[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt バナー](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# How You Got Rich

### 豊かさから充実、そして足るを知ることへ

[![オンラインで読む](https://img.shields.io/badge/読む-オンライン-B94A2F?style=for-the-badge&logo=readme&logoColor=white)](https://lachlanchen.github.io/HowYouGotRich/)
[![フルサイズ PDF](https://img.shields.io/badge/PDF-フルサイズ-18332F?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](../editions/how-you-got-rich.pdf)
[![ポケット PDF](https://img.shields.io/badge/PDF-ポケット_1.2x-CB8A3D?style=for-the-badge&logo=bookstack&logoColor=white)](../editions/how-you-got-rich-pocket-1.2x.pdf)
[![GitHub Sponsors](https://img.shields.io/badge/支援-lachlanchen-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)

<p align="center"><a href="https://lachlanchen.github.io/HowYouGotRich/reader.html"><img src="../assets/cover-page-1.png" alt="How You Got Rich の表紙" width="520"></a></p>

*How You Got Rich* は、人がどのように富を生み、守り、使うのか、そして
富を終わりのない地位競争ではなく自由へ変えるにはどうすればよいのかを
率直に探る本です。School of Hard Knocks のインタビューを人間的かつ
実証的な背骨とし、成功談を失敗、運、出発条件、インセンティブ、
生存者バイアス、他者が負ったコストに照らして検討します。

## より豊かな「富」の定義

| 豊かさ · 富足 | 充実 · 满足 | 足るを知る · 知足 |
| --- | --- | --- |
| 慢性的な欠乏から離れて生きるために十分な資源、能力、関係、時間、回復力、選択肢。 | 努力に値する目的へ仕事と生活を向けること。 | 蓄積に支配される前に「もう十分」と認められる自由。 |

経済的自由は三つのための余白を作れます。しかし、その余白をどう使うか
までは決めてくれません。

## 本を読む

| 形式 | 用途 | 開く |
| --- | --- | --- |
| 書籍サイト | 主題、構成、版、更新情報 | [訪問](https://lachlanchen.github.io/HowYouGotRich/) |
| ブラウザーリーダー | 章ナビゲーション付き全文 | [読む](https://lachlanchen.github.io/HowYouGotRich/reader.html) |
| Web 版 | 成長中のアクセシブルな章表示 | [見る](https://lachlanchen.github.io/HowYouGotRich/book.html) |
| フルサイズ PDF · 163ページ | 印刷、デスクトップ、大型タブレット | [ダウンロード](../editions/how-you-got-rich.pdf) |
| ポケット 1.2x PDF · 349ページ | 電子書籍端末、小型画面、6x9印刷 | [ダウンロード](../editions/how-you-got-rich-pocket-1.2x.pdf) |

V2 は[フルサイズ](../editions/v2/how-you-got-rich-v2.pdf)と
[ポケット 1.2x](../editions/v2/how-you-got-rich-v2-pocket-1.2x.pdf)で恒久保存
されます。バージョンなしのリンクは、出典、編集、組版の審査を通過した版に
のみ更新されます。

## 本の論理

| 部 | 中心となる問い |
| --- | --- |
| I. お金は何のためか | 富はどのような人生を支えるべきか。 |
| II. 価値あるものを作る | 人は何を選び、信頼し、対価を払うのか。 |
| III. 仕組みを所有する | 努力を、創業者より長く残る資産へどう変えるか。 |
| IV. 資本、リスク、時間 | 所有者を壊さずにお金を複利成長させるにはどうするか。 |
| V. 自由と十分 | 生存だけが問題でなくなった後、富は何のためにあるのか。 |

## ビルドと検証

`pdflatex` を含む TeX Live と、`python3`、`rsync`、Poppler、`qpdf` が
必要です。

```bash
make full
make pocket
make verify
make verify-site
make serve
```

サイトのソースは [`docs/`](../docs/)、編集可能な書籍は
[`source/`](../source/) にあります。

## 出典と謝辞

本書は、主に **James Dumoulin** が司会を務める **School of Hard Knocks**
のインタビューと、各出演者が語った経験に基づく独立した統合です。掲載は、
本書の確認や推奨を意味しません。
[`sources/interviews.csv`](../sources/interviews.csv) は、文字起こし自体を
再配布せずに135件の出典を記録しています。

出典忠実性、帰属、論理、文章、アクセシビリティ、組版に関する修正を歓迎
します。[`CONTRIBUTING.md`](../CONTRIBUTING.md) と
[`RIGHTS.md`](../RIGHTS.md) を参照してください。
[LazyingArt](https://lazying.art) と [LazyLearn](https://learn.lazying.art)
が執筆・編集しています。

## 支援

| 寄付 | PayPal | Stripe |
| --- | --- | --- |
| [![寄付](https://img.shields.io/badge/寄付-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-寄付-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 引用

GitHub は [`CITATION.cff`](../CITATION.cff) から引用情報を出力します。

```bibtex
@book{lazyingart2026howyougotrich,
  author    = {{LazyingArt LLC}},
  title     = {How You Got Rich: From Abundance to Fulfillment and Contentment},
  year      = {2026},
  publisher = {LazyingArt and LazyLearn},
  url       = {https://github.com/lachlanchen/HowYouGotRich}
}
```
