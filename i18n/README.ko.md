[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt 배너](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# How You Got Rich

### 풍요에서 성취와 만족, 그리고 충분함을 아는 삶으로

[![온라인 읽기](https://img.shields.io/badge/읽기-온라인-B94A2F?style=for-the-badge&logo=readme&logoColor=white)](https://lachlanchen.github.io/HowYouGotRich/)
[![전체 PDF](https://img.shields.io/badge/PDF-전체_판형-18332F?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](../editions/how-you-got-rich.pdf)
[![포켓 PDF](https://img.shields.io/badge/PDF-포켓_1.2x-CB8A3D?style=for-the-badge&logo=bookstack&logoColor=white)](../editions/how-you-got-rich-pocket-1.2x.pdf)
[![GitHub Sponsors](https://img.shields.io/badge/후원-lachlanchen-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)

<p align="center"><a href="https://lachlanchen.github.io/HowYouGotRich/reader.html"><img src="../assets/cover-page-1.png" alt="How You Got Rich 표지" width="520"></a></p>

*How You Got Rich*는 사람들이 부를 만들고 지키고 사용하는 방식, 그리고
부가 끝없는 지위 경쟁이 아니라 자유가 되는 방식을 솔직하게 탐구합니다.
School of Hard Knocks 인터뷰가 인간적이고 증거에 기반한 중심축을 이룹니다.
성공담은 실패, 운, 출발 조건, 인센티브, 생존자 편향, 다른 사람이 떠안은
비용과 함께 검토됩니다.

## 더 넓은 부의 정의

| 풍요 · 富足 | 성취 · 满足 | 만족과 절제 · 知足 |
| --- | --- | --- |
| 만성적 결핍 없이 살 수 있는 충분한 자원, 역량, 관계, 시간, 회복력, 선택지. | 노력할 가치가 있는 목적에 일과 삶을 사용하는 것. | 축적이 삶을 지배하기 전에 충분함을 알아볼 수 있는 자유. |

경제적 자유는 이 세 가지를 위한 여지를 만들 수 있기에 중요합니다. 그러나
그 여지를 어떻게 쓸지는 결정해 주지 않습니다.

## 책 읽기

| 형식 | 용도 | 열기 |
| --- | --- | --- |
| 책 웹사이트 | 전제, 구조, 판본, 업데이트 | [방문](https://lachlanchen.github.io/HowYouGotRich/) |
| 브라우저 리더 | 부와 장별 탐색이 가능한 전체 책 | [읽기](https://lachlanchen.github.io/HowYouGotRich/reader.html) |
| 웹 판본 | 확장 중인 접근성 높은 장별 보기 | [살펴보기](https://lachlanchen.github.io/HowYouGotRich/book.html) |
| 전체 PDF · 163쪽 | 인쇄, 데스크톱, 큰 태블릿 | [다운로드](../editions/how-you-got-rich.pdf) |
| 포켓 1.2x PDF · 349쪽 | 전자책 단말기, 작은 화면, 6x9 인쇄 | [다운로드](../editions/how-you-got-rich-pocket-1.2x.pdf) |

V2는 [전체 판형](../editions/v2/how-you-got-rich-v2.pdf)과
[포켓 1.2x](../editions/v2/how-you-got-rich-v2-pocket-1.2x.pdf)로 영구 보존됩니다.
버전 표기가 없는 링크는 출처, 편집, 조판 검토를 통과한 뒤에만 갱신됩니다.

## 책의 논리

| 부 | 중심 질문 |
| --- | --- |
| I. 돈은 무엇을 위한 것인가 | 부는 어떤 삶을 지탱해야 하는가? |
| II. 가치 있는 것을 만들기 | 사람들은 무엇을 선택하고 신뢰하며 대가를 지불하는가? |
| III. 기계를 소유하기 | 노력을 창업자보다 오래 남는 자산으로 어떻게 바꿀 수 있는가? |
| IV. 자본, 위험, 시간 | 소유자를 파괴하지 않으면서 돈을 복리로 키우려면 어떻게 해야 하는가? |
| V. 자유와 충분함 | 생존이 유일한 질문이 아니게 된 뒤 부는 무엇을 위한 것인가? |

## 빌드와 검증

`pdflatex`가 포함된 TeX Live와 `python3`, `rsync`, Poppler, `qpdf`가
필요합니다.

```bash
make full
make pocket
make verify
make verify-site
make serve
```

웹사이트 소스는 [`docs/`](../docs/), 편집 가능한 책은
[`source/`](../source/)에 있습니다.

## 출처와 감사의 글

이 책은 주로 **James Dumoulin**이 진행한 **School of Hard Knocks** 인터뷰와
각 출연자가 공유한 경험을 바탕으로 한 독립적인 종합입니다. 출연자의 포함이
책에 대한 검토나 지지를 뜻하지 않습니다.
[`sources/interviews.csv`](../sources/interviews.csv)는 전사문을 재배포하지
않고 135개 출처를 기록합니다.

출처 충실성, 귀속, 논리, 문장, 접근성, 조판에 관한 수정을 환영합니다.
[`CONTRIBUTING.md`](../CONTRIBUTING.md)와 [`RIGHTS.md`](../RIGHTS.md)를
참조하십시오. [LazyingArt](https://lazying.art)와
[LazyLearn](https://learn.lazying.art)이 집필하고 큐레이션했습니다.

## 후원

| 기부 | PayPal | Stripe |
| --- | --- | --- |
| [![기부](https://img.shields.io/badge/기부-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-기부-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 인용

GitHub는 [`CITATION.cff`](../CITATION.cff)를 사용해 인용 정보를 제공합니다.

```bibtex
@book{lazyingart2026howyougotrich,
  author    = {{LazyingArt LLC}},
  title     = {How You Got Rich: From Abundance to Fulfillment and Contentment},
  year      = {2026},
  publisher = {LazyingArt and LazyLearn},
  url       = {https://github.com/lachlanchen/HowYouGotRich}
}
```
