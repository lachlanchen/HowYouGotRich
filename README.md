[English](README.md) · [العربية](i18n/README.ar.md) · [Español](i18n/README.es.md) · [Français](i18n/README.fr.md) · [日本語](i18n/README.ja.md) · [한국어](i18n/README.ko.md) · [Tiếng Việt](i18n/README.vi.md) · [中文 (简体)](i18n/README.zh-Hans.md) · [中文（繁體）](i18n/README.zh-Hant.md) · [Deutsch](i18n/README.de.md) · [Русский](i18n/README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# How You Got Rich

### From Abundance to Fulfillment and Contentment

[![Read online](https://img.shields.io/badge/Read-Online-B94A2F?style=for-the-badge&logo=readme&logoColor=white)](https://lachlanchen.github.io/HowYouGotRich/)
[![Full PDF](https://img.shields.io/badge/PDF-Full_Size-18332F?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](editions/how-you-got-rich.pdf)
[![Pocket PDF](https://img.shields.io/badge/PDF-Pocket_1.2x-CB8A3D?style=for-the-badge&logo=bookstack&logoColor=white)](editions/how-you-got-rich-pocket-1.2x.pdf)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-lachlanchen-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)

<p align="center">
  <a href="https://lachlanchen.github.io/HowYouGotRich/chapters/note-on-the-conversations.html">
    <img src="assets/cover-page-1.png" alt="How You Got Rich cover" width="520">
  </a>
</p>

*How You Got Rich* is a candid investigation of how people create, keep, and
use wealth, and how wealth can become freedom rather than status without an
end. The School of Hard Knocks interviews provide its human and evidentiary
spine. Their success stories are tested against failure, luck, starting
conditions, incentives, survivorship, and costs carried by other people.

## A Richer Definition of Wealth

| Abundance · 富足 | Fulfillment · 满足 | Contentment · 知足 |
| --- | --- | --- |
| Enough resources, capability, relationships, time, resilience, and options. | Work and life directed toward purposes worth the effort. | The freedom to recognize enough before accumulation takes command. |

Financial freedom matters because it can create room for all three. It cannot
decide how that room should be used.

## Read the Book

| Format | Best for | Open |
| --- | --- | --- |
| Native web book | Complete searchable prose, equations, figures, and chapter navigation | [Read](https://lachlanchen.github.io/HowYouGotRich/chapters/note-on-the-conversations.html) |
| Book map | Search all prose or browse the five-part argument | [Explore](https://lachlanchen.github.io/HowYouGotRich/book.html) |
| PDF editions | Optional browser, print, and download formats | [Open](https://lachlanchen.github.io/HowYouGotRich/reader.html) |
| Full-size V3 PDF · 163 pages | Print, desktop, and larger tablets | [Download](editions/how-you-got-rich.pdf) |
| Pocket V3 1.2x PDF · 349 pages | E-readers, compact screens, and 6x9 printing | [Download](editions/how-you-got-rich-pocket-1.2x.pdf) |

V3 is fixed in its [versioned archive](editions/v3/README.md). V2 remains
permanently available as [full size](editions/v2/how-you-got-rich-v2.pdf) and
[pocket 1.2x](editions/v2/how-you-got-rich-v2-pocket-1.2x.pdf). Unversioned links
move only when a later edition has passed source, editorial, and layout review.
See the [edition policy](VERSIONING.md).

## The Argument

| Part | Governing question |
| --- | --- |
| I. What Money Is For | What kind of life should wealth support? |
| II. Make Something Valuable | What will people choose, trust, and pay for? |
| III. Own the Machine | How can effort become an asset that survives you? |
| IV. Capital, Risk, and Time | How should money compound without destroying its owner? |
| V. Freedom and Enough | What is wealth for once survival is no longer the only question? |

The book develops a practical path from a material floor and useful skill to
customer evidence, ownership, systems, capital allocation, downside survival,
stewardship, freedom, and enough. It does not promise that another person's
route can simply be copied.

## Build and Verify

Install TeX Live with `pdflatex`, plus `pandoc`, `python3`, `rsync`, Poppler,
and `qpdf`.

```bash
make full          # full-size PDF
make pocket        # 6x9 pocket PDF
make verify        # publication checks
make web           # regenerate native HTML from accepted TeX
make site          # assemble the native website and PDF downloads
make verify-site   # validate source parity, prose, navigation, and assets
make serve         # preview at http://localhost:8000
```

Generated files stay under `build/`. The website source is in [`docs/`](docs/),
and the editable book is in [`source/`](source/).

## Sources and Acknowledgements

This is an independent synthesis based on interviews produced by **School of
Hard Knocks**, principally hosted by **James Dumoulin**, and on experiences
shared by the individual interviewees. Their inclusion does not imply review
or endorsement.

[`sources/interviews.csv`](sources/interviews.csv) identifies all 135 source
videos and transcript checksums without redistributing the transcripts.
[`sources/figures.csv`](sources/figures.csv) records timestamped attribution for
the documentary frames retained in the current edition.

## Collaboration

Corrections and careful improvements are welcome, especially for source
fidelity, attribution, reasoning, prose, accessibility, and typography. A
useful report names the chapter, source video, timestamp, current wording, and
proposed repair. See [`CONTRIBUTING.md`](CONTRIBUTING.md) and
[`RIGHTS.md`](RIGHTS.md).

Written and curated by [LazyingArt](https://lazying.art) and
[LazyLearn](https://learn.lazying.art). The evidence-rich research project is
[LazyEarn](https://github.com/lachlanchen/LazyEarn).

## Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## Citation

GitHub reads [`CITATION.cff`](CITATION.cff) and provides citation exports.

```bibtex
@book{lazyingart2026howyougotrich,
  author    = {{LazyingArt LLC}},
  title     = {How You Got Rich: From Abundance to Fulfillment and Contentment},
  year      = {2026},
  publisher = {LazyingArt and LazyLearn},
  url       = {https://github.com/lachlanchen/HowYouGotRich}
}
```
