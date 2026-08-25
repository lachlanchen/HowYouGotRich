# Book Source

`book/how-you-got-rich.tex` is the canonical entry point. It draws its shared
packages and macros from `common_preamble.tex`, chapter text from
`book/manuscript/`, documentary images from `book/manuscript/figures/`, and the
text-free cover image from `book/cover/cover-art.png`.

Build through the repository scripts rather than compiling into this folder:

```bash
make full
make pocket
```

Both editions originate from this source. Pocket-specific page geometry and
typographic adjustments are applied only in a disposable compile copy.
