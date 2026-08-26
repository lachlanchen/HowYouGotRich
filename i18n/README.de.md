[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt-Banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# How You Got Rich

### Von Wohlstand zu Erfüllung und Genügsamkeit

[![Online lesen](https://img.shields.io/badge/Lesen-Online-B94A2F?style=for-the-badge&logo=readme&logoColor=white)](https://lachlanchen.github.io/HowYouGotRich/)
[![PDF Großformat](https://img.shields.io/badge/PDF-Großformat-18332F?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](../editions/how-you-got-rich.pdf)
[![PDF Taschenformat](https://img.shields.io/badge/PDF-Taschenformat_1.2x-CB8A3D?style=for-the-badge&logo=bookstack&logoColor=white)](../editions/how-you-got-rich-pocket-1.2x.pdf)
[![GitHub Sponsors](https://img.shields.io/badge/Unterstützen-lachlanchen-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)

<p align="center"><a href="../editions/how-you-got-rich.pdf"><img src="../assets/cover-page-1.png" alt="Cover von How You Got Rich" width="520"></a></p>

*How You Got Rich* untersucht offen, wie Menschen Vermögen schaffen, erhalten
und einsetzen und wie daraus Freiheit statt endloser Statussuche werden kann.
Die Interviews von School of Hard Knocks bilden das menschliche und empirische
Rückgrat. Erfolgsgeschichten werden an Misserfolg, Glück, Ausgangslage,
Anreizen, Survivorship Bias und den von anderen getragenen Kosten geprüft.

## Eine reichere Definition von Reichtum

| Fülle · 富足 | Erfüllung · 满足 | Genügsamkeit · 知足 |
| --- | --- | --- |
| Ausreichende Mittel, Fähigkeiten, Beziehungen, Zeit, Widerstandskraft und Möglichkeiten. | Arbeit und Leben im Dienst von Zielen, die die Mühe wert sind. | Die Freiheit, genug zu erkennen, bevor das Anhäufen die Führung übernimmt. |

Finanzielle Freiheit ist wichtig, weil sie Raum für alle drei schaffen kann.
Sie entscheidet nicht, wie dieser Raum genutzt werden soll.

## Das Buch lesen

| Format | Geeignet für | Öffnen |
| --- | --- | --- |
| Buchwebsite | Grundidee, Aufbau, Ausgaben und Neuigkeiten | [Besuchen](https://lachlanchen.github.io/HowYouGotRich/) |
| Natives Webbuch | Volltextsuche, Formeln, Abbildungen und Kapitelnavigation | [Lesen](https://lachlanchen.github.io/HowYouGotRich/chapters/note-on-the-conversations.html) |
| Buchkarte | Den Volltext durchsuchen oder das Argument in fünf Teilen erkunden | [Erkunden](https://lachlanchen.github.io/HowYouGotRich/book.html) |
| PDF-Ausgaben | Optionale Formate für Bildschirm, Druck und Download | [Öffnen](https://lachlanchen.github.io/HowYouGotRich/reader.html) |
| Großformat-PDF · 163 Seiten | Druck, Desktop und große Tablets | [Herunterladen](../editions/how-you-got-rich.pdf) |
| Taschenformat 1.2x · 349 Seiten | E-Reader, kleine Bildschirme und 6x9-Druck | [Herunterladen](../editions/how-you-got-rich-pocket-1.2x.pdf) |

V2 bleibt dauerhaft als [Großformat](../editions/v2/how-you-got-rich-v2.pdf) und
[Taschenformat 1.2x](../editions/v2/how-you-got-rich-v2-pocket-1.2x.pdf)
erhalten. Unversionierte Links wechseln erst nach Quellen-, Text- und
Layoutprüfung.

## Die Argumentation

| Teil | Leitfrage |
| --- | --- |
| I. Wozu Geld dient | Welche Art von Leben soll Vermögen tragen? |
| II. Etwas Wertvolles schaffen | Was werden Menschen wählen, wem vertrauen und wofür zahlen? |
| III. Die Maschine besitzen | Wie wird Anstrengung zu einem Vermögenswert, der seinen Schöpfer überdauert? |
| IV. Kapital, Risiko und Zeit | Wie kann Geld wachsen, ohne seinen Eigentümer zu zerstören? |
| V. Freiheit und genug | Wozu dient Vermögen, wenn Überleben nicht mehr die einzige Frage ist? |

## Bauen und prüfen

Benötigt werden TeX Live mit `pdflatex`, außerdem `python3`, `rsync`, Poppler
und `qpdf`.

```bash
make full
make pocket
make verify
make verify-site
make serve
```

Die Website liegt in [`docs/`](../docs/), das editierbare Buch in
[`source/`](../source/).

## Quellen und Danksagung

Diese unabhängige Synthese beruht auf Interviews von **School of Hard Knocks**,
überwiegend moderiert von **James Dumoulin**, und auf den Erfahrungen der
Interviewten. Ihre Aufnahme bedeutet keine Prüfung oder Empfehlung.
[`sources/interviews.csv`](../sources/interviews.csv) verzeichnet alle 135
Quellen, ohne Transkripte weiterzugeben.

Korrekturen zu Quellentreue, Zuschreibung, Argumentation, Sprache,
Barrierefreiheit und Typografie sind willkommen. Siehe
[`CONTRIBUTING.md`](../CONTRIBUTING.md) und [`RIGHTS.md`](../RIGHTS.md). Verfasst
und kuratiert von [LazyingArt](https://lazying.art) und
[LazyLearn](https://learn.lazying.art).

## Unterstützung

| Spenden | PayPal | Stripe |
| --- | --- | --- |
| [![Spenden](https://img.shields.io/badge/Spenden-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Spenden-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## Zitieren

GitHub verwendet [`CITATION.cff`](../CITATION.cff) für Zitationsexporte.

```bibtex
@book{lazyingart2026howyougotrich,
  author    = {{LazyingArt LLC}},
  title     = {How You Got Rich: From Abundance to Fulfillment and Contentment},
  year      = {2026},
  publisher = {LazyingArt and LazyLearn},
  url       = {https://github.com/lachlanchen/HowYouGotRich}
}
```
