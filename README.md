# How You Got Rich

<p align="center">
  <a href="editions/how-you-got-rich.pdf">
    <img src="assets/cover-page-1.png" alt="How You Got Rich cover" width="520">
  </a>
</p>

### From Abundance to Fulfillment and Contentment

*How You Got Rich* is a rigorous, candid search for how people become rich,
how wealth is created, kept, and deployed, and how it can become freedom,
abundance, fulfillment, and contentment rather than status without an end.
The School of Hard Knocks interview corpus is its human and evidentiary spine.
Success stories are tested against failures, luck, starting conditions,
incentives, survivorship, and costs carried by other people. The book is
practical without promising that another person's route can simply be copied.

## A Richer Definition of Wealth

| Abundance | Fulfillment | Contentment |
| --- | --- | --- |
| Sufficient resources, capabilities, relationships, time, and options. | Work and life directed toward purposes worth the effort. | The freedom to recognize enough before accumulation takes command. |

Financial freedom matters because it can create room for all three. It cannot
decide how that room should be used.

## What the Book Develops

- A material floor and a clear reason for seeking financial freedom.
- The path from useful skill to customer value, distribution, and trust.
- Ownership, systems, teams, recurring revenue, and transferable enterprise.
- Capital allocation, leverage, compounding, taxes, and downside exposure.
- Practical tests for reversible risk, stewardship, freedom, and enough.

## Structure

| Part | Question |
| --- | --- |
| I. What Money Is For | What kind of life should wealth support? |
| II. Make Something Valuable | What will people choose, trust, and pay for? |
| III. Own the Machine | How can effort become an asset that survives you? |
| IV. Capital, Risk, and Time | How should money compound without destroying its owner? |
| V. Freedom and Enough | What is wealth for once survival is no longer the only question? |

## Editions

| Edition | Best for | Download |
| --- | --- | --- |
| Full size, 162 pages | Print, desktop, and larger tablets | [PDF](editions/how-you-got-rich.pdf) |
| Pocket 1.2x, 312 pages | Compact screens, e-readers, and 6x9 printing | [PDF](editions/how-you-got-rich-pocket-1.2x.pdf) |

The accepted V2 edition is permanently archived as
[full size](editions/v2/how-you-got-rich-v2.pdf) and
[pocket 1.2x](editions/v2/how-you-got-rich-v2-pocket-1.2x.pdf). Unversioned
links always point to the latest accepted edition; publishing a later edition
does not remove V2. See the [edition policy](VERSIONING.md) for the durable
version and repository-history rules.

The editable book lives in [`source/`](source/). The cover preview above is
rendered from page one of the accepted full-size PDF, not from separate cover
art.

## Build and Verify

Install a TeX Live distribution with `pdflatex`, plus `python3`, `rsync`,
Poppler, and `qpdf`. Then run:

```bash
make full
make pocket
make verify
```

Generated files stay under `build/`. The pocket exporter builds from the same
accepted TeX in a separate compile tree; it does not rewrite the source.

## Sources and Acknowledgements

The book is an independent synthesis based on interviews produced by **School
of Hard Knocks**, principally hosted by **James Dumoulin**, and on the
experiences shared by the individual interviewees. Their inclusion does not
imply review or endorsement of this book.

[`sources/interviews.csv`](sources/interviews.csv) identifies all 135 source
videos and records the checksum of each transcript used for the accepted
edition without redistributing the transcripts. The two documentary frames in
the book are timestamped and attributed in
[`sources/figures.csv`](sources/figures.csv).

## Status and Collaboration

This repository publishes the first reader edition. Corrections and careful
improvements are welcome, especially for source fidelity, attribution,
reasoning, prose, accessibility, and typography. A useful correction names the
chapter, source video, timestamp, current wording, and proposed repair. See
[`CONTRIBUTING.md`](CONTRIBUTING.md).

The manuscript and compilation are copyright LazyingArt LLC. The interviews,
video frames, names, and third-party materials remain subject to their
respective rights. Public access to this repository is not an open-content
license; see [`RIGHTS.md`](RIGHTS.md).

Written and curated by [LazyingArt](https://lazying.art) and
[LazyLearn](https://learn.lazying.art). The broader source and research project
is [LazyEarn](https://github.com/lachlanchen/LazyEarn).

## Citation

GitHub can export citation formats from [`CITATION.cff`](CITATION.cff).

```bibtex
@book{lazyingart2026howyougotrich,
  author    = {{LazyingArt LLC}},
  title     = {How You Got Rich: From Abundance to Fulfillment and Contentment},
  year      = {2026},
  publisher = {LazyingArt and LazyLearn},
  url       = {https://github.com/lachlanchen/HowYouGotRich}
}
```
