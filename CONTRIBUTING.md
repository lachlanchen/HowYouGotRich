# Contributing

The goal is a readable, source-faithful book rather than a growing pile of
advice. Contributions should make the argument clearer, truer, more useful, or
more accessible without turning the chapters back into interview summaries.

## Source Corrections

For a story, quotation, number, identity, or attribution correction, include:

1. The chapter and current wording.
2. The source ID or video URL from `sources/interviews.csv`.
3. The timestamp and the relevant spoken context.
4. The proposed wording and why it is more accurate.

Do not infer personal wealth from company revenue, transaction value, paper
valuation, or a reported headline number. Preserve uncertainty when the source
does not settle a fact.

## Editorial Contributions

- Keep the interview corpus as the evidentiary spine.
- Preserve conflicting experiences and material qualifications.
- Prefer mechanisms and decisions over slogans or motivational filler.
- Do not fabricate quotations, causality, credentials, or outcomes.
- Do not submit raw transcripts, videos, private archives, or unlicensed books.
- Keep reader-facing prose free of production notes and processing language.

## Figures

New figures require a source video, exact timestamp, visible-content review,
reason for inclusion, intended placement, natural caption, and rights note.
Generic intros, logos, duplicate poses, and unrelated frames are not accepted.

## Build

```bash
make full
make pocket
make verify
```

Repair layout defects locally. Do not globally shrink type or weaken margins
to hide one bad page. Pull requests should describe the reader-visible change,
source evidence, and validation performed.

## Contribution Rights

By submitting a contribution, you confirm that you have the right to provide
it and authorize LazyingArt LLC to reproduce, modify, publish, and distribute
it as part of this project. See `RIGHTS.md` before contributing.
