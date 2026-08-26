#!/usr/bin/env python3
"""Build separate and aligned EN-JA-ZH PDF editions from reviewed JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from multilingual_common import (
    MANIFEST_PATH,
    load_entry,
    plain_text_from_markdown,
)
from multilingual_render import render_latex_blocks, render_text_tex, tex_escape


ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = ROOT / "build" / "multilingual"
WORK_ROOT = BUILD_ROOT / "work"
PDF_ROOT = BUILD_ROOT / "pdf"
PUBLIC_ROOT = ROOT / "editions" / "languages"
BOOK_ROOT = ROOT / "source" / "book"

LANGUAGE_NAMES = {"en": "English", "ja": "日本語", "zh": "中文"}
SUBTITLES = {
    "en": "From Abundance to Fulfillment and Contentment",
    "ja": "豊かさから充実、そして足るを知るへ",
    "zh": "从富足走向满足与知足",
}
EDITION_LABELS = {
    "en": "English edition",
    "ja": "日本語版",
    "zh": "中文版",
    "all": "English · 日本語 · 中文",
}
PART_TITLES = {
    "I": {
        "en": "What Money Is For",
        "ja": "お金は何のためにあるのか",
        "zh": "金钱为何而存在",
    },
    "II": {
        "en": "Make Something Valuable",
        "ja": "価値あるものをつくる",
        "zh": "创造有价值之物",
    },
    "III": {
        "en": "Own the Machine",
        "ja": "仕組みを所有する",
        "zh": "拥有运转的系统",
    },
    "IV": {
        "en": "Capital, Risk, and Time",
        "ja": "資本、リスク、時間",
        "zh": "资本、风险与时间",
    },
    "V": {
        "en": "Freedom and Enough",
        "ja": "自由と足るを知ること",
        "zh": "自由与知足",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path, log: Path | None = None) -> None:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if log is not None:
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode:
        detail = (completed.stdout + completed.stderr).strip()
        raise RuntimeError(f"command failed ({' '.join(command)}):\n{detail[-6000:]}")


def edition_stem(language: str, pocket: bool) -> str:
    suffix = "en-ja-zh" if language == "all" else language
    pocket_suffix = "-pocket-1.2x" if pocket else ""
    return f"how-you-got-rich-{suffix}{pocket_suffix}"


def localized_frontmatter(language: str) -> tuple[str, str, str, str]:
    if language == "ja":
        return (
            "執筆・編集",
            "School of Hard Knocksが制作し、主にJames Dumoulinが進行したインタビューと、個々の出演者が語った経験に基づく独立した総合・解釈の書である。掲載は、本書の査読や推奨を意味しない。",
            "報告された物語と金額は、それを語った人に帰属する。本書は、個別の投資、税務、法律、保険、医療、または職業上の助言ではない。",
            "多言語読者版 · V3の受理済み本文に基づく",
        )
    if language == "zh":
        return (
            "撰写与编订",
            "本书是一项独立的综合与阐释，依据School of Hard Knocks制作、主要由James Dumoulin主持的访谈，以及各位受访者分享的经历。收录这些内容并不表示他们审阅或认可本书。",
            "书中转述的故事与金额仍归属于讲述它们的人。本书不构成针对个人的投资、税务、法律、保险、医疗或职业建议。",
            "多语读者版 · 基于V3定稿正文",
        )
    return (
        "Written and curated by",
        "Based on interviews produced by School of Hard Knocks, principally hosted by James Dumoulin, and on experiences shared by the individual interviewees. Their inclusion does not imply review or endorsement.",
        "Reported stories and amounts remain attributable to the people who gave them. Nothing in this book is individualized investment, tax, legal, insurance, medical, or career advice.",
        "Multilingual reader edition · based on the accepted V3 text",
    )


def preamble(language: str, pocket: bool) -> str:
    width = "6in" if pocket else "8.5in"
    height = "9in" if pocket else "11in"
    margin = "0.55in" if pocket else "0.9in"
    font_change = r"\usepackage{scrextend}\changefontsizes[16pt]{13.2pt}" if pocket else ""
    cjk_main = "Noto Serif CJK JP" if language == "ja" else "Noto Serif CJK SC"
    if language == "all":
        cjk_main = "Noto Serif CJK SC"
    if pocket:
        running_heads = r"""\fancyhead[LO]{\parbox[b]{0.72\textwidth}{\raggedright\footnotesize\itshape\nouppercase{\leftmark}}}
\fancyhead[RE]{\parbox[b]{0.72\textwidth}{\raggedleft\footnotesize\itshape\nouppercase{\leftmark}}}
\setlength{\headheight}{36pt}"""
    else:
        running_heads = r"""\fancyhead[LO]{\small\itshape\nouppercase{\leftmark}}
\fancyhead[RE]{\small\scshape How You Got Rich}
\setlength{\headheight}{22pt}"""
    return rf"""\documentclass[11pt,twoside,openright]{{book}}
\usepackage[paperwidth={width},paperheight={height},inner={margin},outer={margin},top={margin},bottom={margin}]{{geometry}}
\usepackage{{luatexja-fontspec}}
\usepackage{{luatexja-ruby}}
\usepackage{{xparse}}
\usepackage{{microtype}}
\usepackage{{amsmath,amssymb,amsthm,mathtools,bm}}
\usepackage{{graphicx}}
\usepackage{{xcolor}}
\usepackage{{booktabs,array,longtable}}
\usepackage{{enumitem}}
\usepackage{{float,caption}}
\usepackage{{hyperref}}
\usepackage{{fancyhdr}}
\usepackage{{tikz}}
\usepackage{{titlesec}}
\usepackage{{xurl}}
\usepackage{{emptypage}}
\usepackage{{adjustbox}}
{font_change}

\setmainfont{{TeX Gyre Pagella}}
\setsansfont{{Noto Sans}}
\setmonofont{{TeX Gyre Cursor}}
\setmainjfont{{{cjk_main}}}
\setsansjfont{{Noto Sans CJK SC}}
\newjfontfamily\jpfont{{Noto Serif CJK JP}}
\newjfontfamily\zhfont{{Noto Serif CJK SC}}

\definecolor{{wealthink}}{{HTML}}{{191A24}}
\definecolor{{wealthfire}}{{HTML}}{{C7502A}}
\definecolor{{wealthgold}}{{HTML}}{{9A783D}}
\definecolor{{wealthpaper}}{{HTML}}{{F3EFE4}}
\definecolor{{japaneseink}}{{HTML}}{{335F57}}
\definecolor{{chineseink}}{{HTML}}{{8A3B29}}
\hypersetup{{
  pdftitle={{How You Got Rich}},
  pdfauthor={{LazyingArt · LazyLearn}},
  pdfsubject={{{tex_escape(SUBTITLES.get(language, SUBTITLES['en']))}}},
  colorlinks=true,
  linkcolor=wealthfire!75!black,
  urlcolor=wealthfire!75!black
}}

\graphicspath{{{{assets/}}}}
\setkeys{{Gin}}{{width=\linewidth,keepaspectratio}}
\setlength{{\parindent}}{{1.05em}}
\setlength{{\parskip}}{{0.22em}}
\setlength{{\emergencystretch}}{{2.4em}}
\linespread{{1.22}}
\renewcommand{{\arraystretch}}{{1.35}}
\setlength{{\extrarowheight}}{{2pt}}
\setlength{{\LTleft}}{{0pt}}
\setlength{{\LTright}}{{0pt}}
\setlist[itemize]{{topsep=0.35em,itemsep=0.25em,leftmargin=*}}
\setlist[enumerate]{{topsep=0.35em,itemsep=0.25em,leftmargin=*}}
\raggedbottom
\sloppy
\providecommand{{\tightlist}}{{\setlength{{\itemsep}}{{0.2em}}\setlength{{\parskip}}{{0pt}}}}

\ltjsetruby{{size=0.45,mode=1,intergap=0.08,rubysmash=false}}
\NewDocumentCommand{{\jpruby}}{{m m}}{{\ltjruby[fontcmd=\jpfont]{{{{\jpfont #1}}}}{{#2}}}}
\NewDocumentCommand{{\zhpy}}{{m m}}{{\ltjruby[fontcmd=\sffamily]{{{{\zhfont #1}}}}{{#2}}}}

\titleformat{{\chapter}}[display]
  {{\normalfont\color{{wealthink}}}}
  {{\Large\scshape\color{{wealthgold}}\chaptertitlename\ \thechapter}}
  {{0.55em}}{{\Huge\bfseries\raggedright}}
  [\vspace{{0.7em}}{{\color{{wealthfire}}\titlerule[1.1pt]}}]
\titleformat{{name=\chapter,numberless}}[display]
  {{\normalfont\color{{wealthink}}}}{{}}{{0pt}}{{\Huge\bfseries\raggedright}}
  [\vspace{{0.7em}}{{\color{{wealthfire}}\titlerule[1.1pt]}}]
\titlespacing*{{\chapter}}{{0pt}}{{-16pt}}{{24pt}}
\titleformat{{\section}}{{\normalfont\Large\bfseries\color{{wealthink}}}}{{\thesection}}{{0.7em}}{{}}
\titleformat{{name=\section,numberless}}{{\normalfont\Large\bfseries\color{{wealthink}}}}{{}}{{0pt}}{{}}

\makeatletter
\renewcommand{{\chaptermark}}[1]{{\markboth{{\thechapter\enspace #1}}{{}}}}
\renewcommand{{\sectionmark}}[1]{{}}
\makeatother
\fancyhf{{}}
\fancyhead[LE,RO]{{\small\thepage}}
{running_heads}
\renewcommand{{\headrulewidth}}{{0.45pt}}
\fancypagestyle{{plain}}{{\fancyhf{{}}\fancyhead[LE,RO]{{\small\thepage}}\renewcommand{{\headrulewidth}}{{0pt}}}}

\newcommand{{\ChapterQuestion}}[1]{{\begin{{quote}}\centering\itshape\color{{wealthink!75}}#1\end{{quote}}}}
\newenvironment{{AlignedUnit}}{{\par\medskip\begingroup}}{{\endgroup\par\medskip}}
\newenvironment{{EnglishLayer}}{{\par\noindent\textcolor{{wealthgold}}{{\sffamily\scriptsize\bfseries ENGLISH}}\par\smallskip}}{{\par}}
\newenvironment{{JapaneseLayer}}{{\par\noindent\textcolor{{japaneseink}}{{\sffamily\scriptsize\bfseries 日本語}}\par\smallskip\jpfont\color{{japaneseink}}}}{{\par}}
\newenvironment{{ChineseLayer}}{{\par\noindent\textcolor{{chineseink}}{{\sffamily\scriptsize\bfseries 中文}}\par\smallskip\zhfont\color{{chineseink}}}}{{\par}}
\newcommand{{\AlignedHeading}}[2]{{\par\nopagebreak\smallskip{{\jpfont\color{{japaneseink}}#1}}\par{{\zhfont\color{{chineseink}}#2}}\par\medskip}}
\newcommand{{\AlignedCaption}}[3]{{\par\noindent\textcolor{{#1}}{{\sffamily\scriptsize\bfseries #2}}\enspace #3\par}}
"""


def title_page(language: str, pocket: bool) -> str:
    title_size = "28" if pocket else "38"
    title_leading = "31" if pocket else "42"
    subtitle = SUBTITLES["en"] if language == "all" else SUBTITLES[language]
    local_lines = ""
    if language == "all":
        local_lines = (
            r"\vspace{0.55em}{\normalsize\jpfont\color{wealthink!78}"
            + tex_escape(SUBTITLES["ja"])
            + r"\par}{\normalsize\zhfont\color{wealthink!78}"
            + tex_escape(SUBTITLES["zh"])
            + r"\par}"
        )
    return rf"""\begin{{titlepage}}
\thispagestyle{{empty}}
\begin{{tikzpicture}}[remember picture,overlay]
  \node[anchor=center,inner sep=0] at (current page.center) {{\includegraphics[height=\paperheight]{{cover-art.png}}}};
  \node[anchor=north east,align=right,text width=0.64\paperwidth,inner sep=0pt]
    at ([xshift=-0.07\paperwidth,yshift=-0.07\paperheight]current page.north east) {{%
      {{\fontsize{{{title_size}}}{{{title_leading}}}\selectfont\bfseries\color{{wealthink}} HOW YOU\\GOT RICH\par}}
      \vspace{{0.85em}}{{\large\itshape\color{{wealthink!78}} {tex_escape(subtitle)}\par}}
      {local_lines}
      \vspace{{0.9em}}{{\small\sffamily\bfseries\color{{wealthfire}} {tex_escape(EDITION_LABELS[language])}\par}}
    }};
  \node[anchor=south east,align=right,text width=0.60\paperwidth,inner sep=0pt]
    at ([xshift=-0.07\paperwidth,yshift=0.06\paperheight]current page.south east) {{%
      {{\large\bfseries\color{{wealthink}}\href{{https://lazying.art}}{{LazyingArt}} $\boldsymbol{{\cdot}}$ \href{{https://learn.lazying.art}}{{LazyLearn}}\par}}
    }};
\end{{tikzpicture}}
\mbox{{}}
\end{{titlepage}}
"""


def copyright_page(language: str) -> str:
    if language == "all":
        lead, basis, caution, edition = localized_frontmatter("en")
        ja = localized_frontmatter("ja")
        zh = localized_frontmatter("zh")
        body = rf"""{tex_escape(basis)}

\medskip{{\jpfont {tex_escape(ja[1])}}}

\medskip{{\zhfont {tex_escape(zh[1])}}}

\bigskip {tex_escape(caution)}

\medskip{{\jpfont {tex_escape(ja[2])}}}

\medskip{{\zhfont {tex_escape(zh[2])}}}"""
    else:
        lead, basis, caution, edition = localized_frontmatter(language)
        body = tex_escape(basis) + "\n\n\\bigskip\n" + tex_escape(caution)
    return rf"""\cleardoublepage
\thispagestyle{{empty}}
\vspace*{{0.10\textheight}}
{{\Huge\bfseries How You Got Rich\par}}
\vspace{{0.6em}}
{{\Large\itshape {tex_escape(SUBTITLES['en'] if language == 'all' else SUBTITLES[language])}\par}}
\vfill
{{\large {tex_escape(lead)}\\[0.25em]\href{{https://lazying.art}}{{LazyingArt}} $\boldsymbol{{\cdot}}$ \href{{https://learn.lazying.art}}{{LazyLearn}}\par}}
\vspace{{1.6em}}
{body}
\vfill
{{\small Copyright \textcopyright\ 2026 LazyingArt LLC.\\{tex_escape(edition)}.\\
\href{{https://lazying.art}}{{lazying.art}} $\boldsymbol{{\cdot}}$ \href{{https://learn.lazying.art}}{{learn.lazying.art}}\par}}
\cleardoublepage
"""


def chapter_title(entry: dict[str, Any], language: str) -> str:
    if language == "all":
        return tex_escape(entry["metadata"]["title"]["en"])
    return tex_escape(entry["metadata"]["title"][language])


def chapter_question(entry: dict[str, Any], language: str) -> str:
    if language == "all":
        lines = []
        for code in ("en", "ja", "zh"):
            rendered = render_text_tex(entry["metadata"]["question"][code], code)
            font = {"en": "", "ja": r"\jpfont ", "zh": r"\zhfont "}[code]
            lines.append("{" + font + rendered + r"\par}")
        return "\n".join(lines)
    return render_text_tex(entry["metadata"]["question"][language], language)


def separate_entry_tex(entry: dict[str, Any], language: str, blocks: dict[str, str]) -> str:
    title = chapter_title(entry, language)
    if entry["kind"] == "chapter":
        opening = rf"\chapter{{{title}}}\ChapterQuestion{{{chapter_question(entry, language)}}}"
    else:
        opening = rf"\chapter*{{{title}}}\addcontentsline{{toc}}{{chapter}}{{{title}}}\ChapterQuestion{{{chapter_question(entry, language)}}}"
    body = "\n\n".join(blocks[str(block["id"])] for block in entry["blocks"])
    font = {"ja": r"\jpfont ", "zh": r"\zhfont "}.get(language, "")
    return opening + "\n\n{" + font + "\n" + body + "\n}\n"


def combined_block_tex(
    block: dict[str, Any], rendered: dict[str, dict[str, str]]
) -> str:
    block_id = str(block["id"])
    kind = str(block["kind"])
    if kind == "Header":
        english = rendered["en"][block_id]
        ja = render_text_tex(plain_text_from_markdown(block["ja"]["markdown"]), "ja")
        zh = render_text_tex(plain_text_from_markdown(block["zh"]["markdown"]), "zh")
        return english + rf"\AlignedHeading{{{ja}}}{{{zh}}}"

    protected_types = [str(item.get("type")) for item in block.get("protected", [])]
    source_plain = plain_text_from_markdown(block["en"]["markdown"])
    if protected_types and set(protected_types) == {"math"} and not source_plain:
        return rendered["en"][block_id]

    if "image" in protected_types:
        ja_caption = render_text_tex(plain_text_from_markdown(block["ja"]["markdown"]), "ja")
        zh_caption = render_text_tex(plain_text_from_markdown(block["zh"]["markdown"]), "zh")
        captions = (
            rf"\AlignedCaption{{japaneseink}}{{日本語}}{{{{\jpfont {ja_caption}}}}}"
            + rf"\AlignedCaption{{chineseink}}{{中文}}{{{{\zhfont {zh_caption}}}}}"
        )
        figure = rendered["en"][block_id]
        if r"\end{figure}" not in figure:
            raise ValueError(f"{block_id}: image block did not render as a figure")
        return figure.rsplit(r"\end{figure}", 1)[0] + captions + r"\end{figure}"

    return rf"""\begin{{AlignedUnit}}
\begin{{EnglishLayer}}
{rendered['en'][block_id]}
\end{{EnglishLayer}}
\begin{{JapaneseLayer}}
{rendered['ja'][block_id]}
\end{{JapaneseLayer}}
\begin{{ChineseLayer}}
{rendered['zh'][block_id]}
\end{{ChineseLayer}}
\end{{AlignedUnit}}"""


def combined_entry_tex(entry: dict[str, Any], rendered: dict[str, dict[str, str]]) -> str:
    title = chapter_title(entry, "all")
    ja_title = tex_escape(entry["metadata"]["title"]["ja"])
    zh_title = tex_escape(entry["metadata"]["title"]["zh"])
    if entry["kind"] == "chapter":
        opening = rf"\chapter{{{title}}}\AlignedHeading{{{ja_title}}}{{{zh_title}}}\ChapterQuestion{{{chapter_question(entry, 'all')}}}"
    else:
        opening = rf"\chapter*{{{title}}}\addcontentsline{{toc}}{{chapter}}{{{title}}}\AlignedHeading{{{ja_title}}}{{{zh_title}}}\ChapterQuestion{{{chapter_question(entry, 'all')}}}"
    body = "\n\n".join(combined_block_tex(block, rendered) for block in entry["blocks"])
    return opening + "\n\n" + body + "\n"


def part_tex(part_number: str, language: str) -> str:
    titles = PART_TITLES[part_number]
    if language == "all":
        return rf"\part{{{tex_escape(titles['en'])}\\[0.5em]{{\Large\jpfont {tex_escape(titles['ja'])}}}\\[0.25em]{{\Large\zhfont {tex_escape(titles['zh'])}}}}}"
    return rf"\part{{{tex_escape(titles[language])}}}"


def build_tex(entries: list[dict[str, Any]], language: str, pocket: bool) -> str:
    languages = ("en", "ja", "zh") if language == "all" else (language,)
    rendered_by_entry: dict[str, dict[str, dict[str, str]]] = {}
    for index, entry in enumerate(entries, start=1):
        print(f"render {language} {'pocket' if pocket else 'full'}: {entry['id']} ({index}/{len(entries)})", flush=True)
        rendered_by_entry[entry["id"]] = {
            code: render_latex_blocks(entry, code) for code in languages
        }

    pieces = [
        preamble(language, pocket),
        r"\begin{document}",
        r"\frontmatter\hypersetup{pageanchor=false}",
        title_page(language, pocket),
        copyright_page(language),
    ]
    preface = entries[0]
    introduction = entries[1]
    if language == "all":
        pieces.append(combined_entry_tex(preface, rendered_by_entry[preface["id"]]))
    else:
        pieces.append(separate_entry_tex(preface, language, rendered_by_entry[preface["id"]][language]))
    pieces.extend([r"\hypersetup{pageanchor=true}", r"\tableofcontents", r"\mainmatter"])
    if language == "all":
        pieces.append(combined_entry_tex(introduction, rendered_by_entry[introduction["id"]]))
    else:
        pieces.append(separate_entry_tex(introduction, language, rendered_by_entry[introduction["id"]][language]))

    current_part = None
    for entry in entries[2:]:
        part = entry["part"]["number"]
        if part != current_part:
            pieces.append(part_tex(part, language))
            current_part = part
        if language == "all":
            pieces.append(combined_entry_tex(entry, rendered_by_entry[entry["id"]]))
        else:
            pieces.append(separate_entry_tex(entry, language, rendered_by_entry[entry["id"]][language]))
    pieces.append(r"\end{document}")
    return "\n\n".join(pieces) + "\n"


def prepare_work(stem: str, tex: str) -> tuple[Path, Path]:
    work = WORK_ROOT / stem
    if work.exists():
        shutil.rmtree(work)
    assets = work / "assets"
    output = work / "output"
    assets.mkdir(parents=True)
    output.mkdir(parents=True)
    shutil.copy2(BOOK_ROOT / "cover" / "cover-art.png", assets / "cover-art.png")
    for figure in (BOOK_ROOT / "manuscript" / "figures").iterdir():
        if figure.is_file():
            shutil.copy2(figure, assets / figure.name)
    tex_path = work / f"{stem}.tex"
    tex_path.write_text(tex, encoding="utf-8")
    return work, tex_path


def actionable_overfull(log_text: str) -> list[str]:
    issues = []
    for line in log_text.splitlines():
        match = re.search(r"Overfull \\[hv]box \(([-0-9.]+)pt too (?:wide|high)\)", line)
        if match and float(match.group(1)) > 1.0:
            issues.append(line.strip())
    return issues


def compile_edition(entries: list[dict[str, Any]], language: str, pocket: bool) -> Path:
    stem = edition_stem(language, pocket)
    tex = build_tex(entries, language, pocket)
    work, tex_path = prepare_work(stem, tex)
    output = work / "output"
    for pass_number in (1, 2, 3):
        log = BUILD_ROOT / "logs" / f"{stem}-pass-{pass_number}.log"
        run(
            [
                "lualatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                f"-output-directory={output}",
                tex_path.name,
            ],
            cwd=work,
            log=log,
        )
    pdf = output / f"{stem}.pdf"
    if not pdf.is_file() or not pdf.stat().st_size:
        raise RuntimeError(f"LuaLaTeX did not produce {pdf}")
    final_log = (BUILD_ROOT / "logs" / f"{stem}-pass-3.log").read_text(encoding="utf-8")
    overfull = actionable_overfull(final_log)
    if overfull:
        raise RuntimeError(f"{stem} has actionable overflow:\n" + "\n".join(overfull[:30]))
    run(["qpdf", "--check", str(pdf)], cwd=work)
    PDF_ROOT.mkdir(parents=True, exist_ok=True)
    built = PDF_ROOT / f"{stem}.pdf"
    shutil.copy2(pdf, built)
    print(f"built {built} ({sha256(built)})", flush=True)
    return built


def publish_outputs(outputs: list[Path]) -> None:
    PUBLIC_ROOT.mkdir(parents=True, exist_ok=True)
    for output in outputs:
        shutil.copy2(output, PUBLIC_ROOT / output.name)

    checksums = []
    for pdf in sorted(PUBLIC_ROOT.glob("*.pdf")):
        checksums.append(f"{sha256(pdf)}  {pdf.name}")
    (PUBLIC_ROOT / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")


def copy_english_outputs() -> list[Path]:
    PDF_ROOT.mkdir(parents=True, exist_ok=True)
    pairs = [
        (ROOT / "editions" / "how-you-got-rich.pdf", PDF_ROOT / "how-you-got-rich-en.pdf"),
        (
            ROOT / "editions" / "how-you-got-rich-pocket-1.2x.pdf",
            PDF_ROOT / "how-you-got-rich-en-pocket-1.2x.pdf",
        ),
    ]
    for source, target in pairs:
        if not source.is_file():
            raise RuntimeError(f"accepted English edition is missing: {source}")
        shutil.copy2(source, target)
    return [target for _, target in pairs]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--only",
        action="append",
        choices=[
            "ja-full",
            "ja-pocket",
            "zh-full",
            "zh-pocket",
            "all-full",
            "all-pocket",
        ],
        default=[],
    )
    parser.add_argument("--no-publish", action="store_true")
    parser.add_argument(
        "--publish-existing",
        action="store_true",
        help="publish the complete, already-built PDF set without recompiling",
    )
    args = parser.parse_args()

    validation = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_multilingual.py"), "--require-complete"],
        cwd=ROOT,
        check=False,
    )
    if validation.returncode:
        return validation.returncode

    if args.publish_existing:
        if args.only or args.no_publish:
            parser.error("--publish-existing cannot be combined with --only or --no-publish")
        stems = [
            "how-you-got-rich-en",
            "how-you-got-rich-en-pocket-1.2x",
            "how-you-got-rich-ja",
            "how-you-got-rich-ja-pocket-1.2x",
            "how-you-got-rich-zh",
            "how-you-got-rich-zh-pocket-1.2x",
            "how-you-got-rich-en-ja-zh",
            "how-you-got-rich-en-ja-zh-pocket-1.2x",
        ]
        outputs = [PDF_ROOT / f"{stem}.pdf" for stem in stems]
        missing = [str(path) for path in outputs if not path.is_file() or not path.stat().st_size]
        if missing:
            raise RuntimeError("cannot publish an incomplete PDF set:\n" + "\n".join(missing))
        publish_outputs(outputs)
        print(f"published {len(outputs)} existing PDFs under {PUBLIC_ROOT}")
        return 0

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = [load_entry(item["id"]) for item in manifest["entries"]]
    requested = args.only or [
        "ja-full",
        "ja-pocket",
        "zh-full",
        "zh-pocket",
        "all-full",
        "all-pocket",
    ]
    outputs = copy_english_outputs()
    for item in requested:
        language, shape = item.split("-", 1)
        outputs.append(compile_edition(entries, language, shape == "pocket"))
    if not args.no_publish:
        publish_outputs(outputs)
        print(f"published {len(outputs)} PDFs under {PUBLIC_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
