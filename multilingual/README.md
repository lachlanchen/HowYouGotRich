# Multilingual Editions

This directory is the durable English-Japanese-Chinese source for the book's
multilingual PDF and native web editions. All 25 readings and 1,164 stable
blocks are translated and reviewed; the accepted V3 English manuscript remains
the alignment spine.

Each file under `entries/` represents one reading. A stable block records the
exact English Markdown, its source hash and protected math/link/image payload,
then aligned Japanese and modern Chinese. Japanese tokens carry furigana only
when a token contains kanji; Chinese tokens carry pinyin on the corresponding
Chinese token. Rendering is separate from translation so every edition uses
the same reviewed language data.

Prepare or check the English spine with:

```sh
python3 scripts/prepare_multilingual.py
python3 scripts/prepare_multilingual.py --check
```

Translate one reading or inspect resumable progress with:

```sh
python3 scripts/translate_multilingual.py --entry introduction --dry-run
python3 scripts/translate_multilingual.py --entry introduction --commit
make multilingual-status
```

`scripts/run_multilingual_queue.sh` processes all remaining readings with
`gpt-5.6-sol` at `xhigh` reasoning by default. Every accepted reading is
validated, committed, and pushed before the queue advances. Runtime prompts,
responses, and logs stay under ignored `multilingual/runtime/`.

Generated translations must preserve block structure, equations, image paths,
URLs, names, numbers, qualifications, and attribution. A target block is not
publishable until deterministic validation and contextual review both pass.

Install the deterministic annotation dependencies and build every edition with:

```sh
python3 -m pip install -r requirements-multilingual.txt
make multilingual-validate
make multilingual-pdfs
make web
```

PDF generation uses LuaLaTeX, `luatexja-ruby`, Noto CJK fonts, Pandoc, Poppler,
and qpdf. The outputs under `editions/languages/` are separate English,
Japanese, and Chinese books plus an aligned EN-JA-ZH maximum-language book,
each in full-size and 6x9 pocket form. The native reader offers EN, 日本語,
中文, and Together modes from the same JSON. `make sync-multilingual` copies
only accepted PDFs to the LazyEarn Nutstore share using atomic, checksum-verified
replacement; no HTML is synchronized there.
