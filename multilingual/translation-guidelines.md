# Translation Contract

The accepted English V3 is the source of meaning and structure. Translate it
fully into natural modern Japanese and Simplified Chinese without summarizing,
expanding, moralizing, or smoothing away uncertainty and disagreement.

- Preserve every block ID exactly once and in order.
- Preserve Markdown block type and list-item count.
- Preserve all equations, variables, image paths, URLs, code, timestamps,
  numbers, names, qualifications, and attribution.
- Keep personal and organization names in their source Latin spelling unless a
  well-established localized form is unambiguous. Never invent credentials,
  outcomes, quotations, or causal claims.
- Translate headings, captions, emphasis, exercises, and questions as prose,
  while leaving protected payloads unchanged.
- Write lucid nonfiction, not translationese, promotional copy, or a literal
  word-for-word gloss. Keep the source's candid, careful tone and paragraph
  rhythm.
- Use `豊かさ`, `充実`, and `足るを知る` for the central Japanese movement when
  context permits. Use `富足`, `满足`, and `知足` in Chinese. Preserve the
  distinction among resources, meaningful direction, and knowing enough.
- Render financial freedom as `経済的自由` in Japanese and `财务自由` in
  Chinese where that is the intended concept.
- Return only the requested JSON. Do not mention tools, models, prompts,
  processing, or repository paths in translated prose.

Japanese furigana and Chinese pinyin are generated deterministically after the
translation. Translation output must not add parenthetical readings itself.
