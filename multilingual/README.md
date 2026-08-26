# Multilingual Editions

This directory is the durable English–Japanese–Chinese source for the book's
multilingual PDF and web editions. The accepted V3 English manuscript remains
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

Planned outputs are separate English, Japanese, and Chinese books; an aligned
EN–JA–ZH maximum-language book; and a native web reader with monolingual and
combined modes. Nutstore receives PDFs only.
