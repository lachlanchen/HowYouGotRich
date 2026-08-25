# Website

This directory contains the source for the *How You Got Rich* website. The
published site combines three reader-facing forms:

- `index.html`: premise, philosophy, editions, and book structure;
- `reader.html`: the complete accepted PDFs with chapter navigation;
- `book.html`: a data-driven web edition that can receive accepted chapter
  text without changing the site's navigation model.

`data/book.json` is the public navigation manifest. Its chapter order and PDF
page targets must match the accepted edition. The TeX manuscript remains the
canonical prose source until a chapter-parity exporter is accepted.

Build and validate locally from the repository root:

```bash
make verify-site
make serve
```

The build copies the accepted PDFs and cover preview into `build/site/`; it
does not duplicate those binaries in this directory. GitHub Pages deploys the
same assembled tree through `.github/workflows/pages.yml`.
