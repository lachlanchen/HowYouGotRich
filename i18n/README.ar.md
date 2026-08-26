[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![شعار LazyingArt](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# How You Got Rich

### من الوفرة إلى الإنجاز والقناعة

[![اقرأ على الويب](https://img.shields.io/badge/Read-Online-B94A2F?style=for-the-badge&logo=readme&logoColor=white)](https://lachlanchen.github.io/HowYouGotRich/)
[![PDF كامل](https://img.shields.io/badge/PDF-Full_Size-18332F?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](../editions/how-you-got-rich.pdf)
[![PDF جيب](https://img.shields.io/badge/PDF-Pocket_1.2x-CB8A3D?style=for-the-badge&logo=bookstack&logoColor=white)](../editions/how-you-got-rich-pocket-1.2x.pdf)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-lachlanchen-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)

<p align="center"><a href="../editions/how-you-got-rich.pdf"><img src="../assets/cover-page-1.png" alt="غلاف How You Got Rich" width="520"></a></p>

يبحث *How You Got Rich* بصراحة في كيفية صنع الثروة والحفاظ عليها واستخدامها،
وكيف يمكن أن تتحول إلى حرية بدلا من سعي لا ينتهي وراء المكانة. تشكل مقابلات
School of Hard Knocks العمود الفقري الإنساني والاستدلالي للكتاب. وتختبر قصص
النجاح في ضوء الفشل والحظ وظروف البداية والحوافز وانحياز البقاء والتكاليف التي
يتحملها الآخرون.

## تعريف أوسع للثروة

| الوفرة · 富足 | الإنجاز · 满足 | القناعة · 知足 |
| --- | --- | --- |
| موارد وقدرات وعلاقات ووقت ومرونة وخيارات تكفي لحياة بلا ندرة مزمنة. | توجيه العمل والحياة إلى غايات تستحق الجهد. | حرية معرفة متى يكفي، قبل أن يصبح التراكم هو المتحكم. |

تهم الحرية المالية لأنها قد تفتح مجالا للثلاثة جميعا، لكنها لا تحدد كيف ينبغي
استخدام هذا المجال.

## قراءة الكتاب

| الصيغة | الأنسب لها | الرابط |
| --- | --- | --- |
| موقع الكتاب | الفكرة والبنية والإصدارات والتحديثات | [زيارة](https://lachlanchen.github.io/HowYouGotRich/) |
| كتاب ويب أصلي | النص الكامل القابل للبحث والمعادلات والصور والتنقل | [قراءة](https://lachlanchen.github.io/HowYouGotRich/chapters/note-on-the-conversations.html) |
| خريطة الكتاب | البحث في النص أو استكشاف الحجة في خمسة أجزاء | [استكشاف](https://lachlanchen.github.io/HowYouGotRich/book.html) |
| إصدارات PDF | صيغ اختيارية للعرض والطباعة والتنزيل | [فتح](https://lachlanchen.github.io/HowYouGotRich/reader.html) |
| PDF كامل · 163 صفحة | الطباعة والحاسوب والأجهزة اللوحية الكبيرة | [تنزيل](../editions/how-you-got-rich.pdf) |
| PDF جيب 1.2x · 349 صفحة | القارئات والشاشات الصغيرة وطباعة 6x9 | [تنزيل](../editions/how-you-got-rich-pocket-1.2x.pdf) |

يبقى الإصدار V2 محفوظا بالحجم [الكامل](../editions/v2/how-you-got-rich-v2.pdf)
وبنسخة [الجيب 1.2x](../editions/v2/how-you-got-rich-v2-pocket-1.2x.pdf). ولا تنتقل
الروابط غير المرقمة إلى إصدار جديد إلا بعد مراجعة المصادر والتحرير والتنسيق.

## حجة الكتاب

| الجزء | السؤال الناظم |
| --- | --- |
| I. ما الغرض من المال | أي نوع من الحياة ينبغي للثروة أن تدعمه؟ |
| II. اصنع شيئا ذا قيمة | ما الذي سيختاره الناس ويثقون به ويدفعون مقابله؟ |
| III. امتلك الآلة | كيف يتحول الجهد إلى أصل يبقى بعد صاحبه؟ |
| IV. رأس المال والمخاطر والزمن | كيف ينمو المال من غير أن يدمر مالكه؟ |
| V. الحرية والكفاية | ما الغرض من الثروة حين لا يعود البقاء هو السؤال الوحيد؟ |

## البناء والتحقق

ثبت TeX Live مع `pdflatex`، إضافة إلى `python3` و`rsync` وPoppler و`qpdf`.

```bash
make full
make pocket
make verify
make verify-site
make serve
```

مصدر الموقع في [`docs/`](../docs/)، ومصدر الكتاب القابل للتحرير في
[`source/`](../source/).

## المصادر والشكر

هذا عمل تركيبي مستقل يستند إلى مقابلات **School of Hard Knocks** التي يقدم
معظمها **James Dumoulin**، وإلى خبرات الضيوف أنفسهم. لا يعني إدراجهم أنهم
راجعوا الكتاب أو أيدوه. يسجل
[`sources/interviews.csv`](../sources/interviews.csv) المصادر الـ135 من غير
إعادة نشر النصوص المفرغة.

نرحب بالتصحيحات المتعلقة بدقة المصادر والنسب والاستدلال والأسلوب وإتاحة
الوصول والطباعة. راجع [`CONTRIBUTING.md`](../CONTRIBUTING.md) و
[`RIGHTS.md`](../RIGHTS.md). كتب وحرر العمل
[LazyingArt](https://lazying.art) و[LazyLearn](https://learn.lazying.art).

## الدعم

| تبرع | PayPal | Stripe |
| --- | --- | --- |
| [![تبرع](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## الاستشهاد

يستخدم GitHub ملف [`CITATION.cff`](../CITATION.cff) لتصدير بيانات الاستشهاد.

```bibtex
@book{lazyingart2026howyougotrich,
  author    = {{LazyingArt LLC}},
  title     = {How You Got Rich: From Abundance to Fulfillment and Contentment},
  year      = {2026},
  publisher = {LazyingArt and LazyLearn},
  url       = {https://github.com/lachlanchen/HowYouGotRich}
}
```
