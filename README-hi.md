# dsh-safety-brief-check — सुरक्षा तकनीकी ब्रीफिंग रिकॉर्ड की पूर्णता और हस्ताक्षर-समापन की जाँच

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-safety-brief-check` एक 安全技术交底记录 पढ़ता है — उसके हेडर फ़ील्ड, 被交底人 और 签字 की सूचियाँ, और 工种 की सूचियाँ — और उसी रिकॉर्ड की पूर्णता तथा बंद-लूप की जाँच करता है: आपके फ़ॉर्म में माँगे गए कॉलम भरे हैं या नहीं, हर ब्रीफ किया गया व्यक्ति हस्ताक्षरकर्ताओं में दिखता है और कोई दो बार हस्ताक्षर नहीं करता, 交底日期 施工日期 से बाद की नहीं है, काम करने वाले 工种 ब्रीफ किए गए 工种 की सूची में आते हैं, रिकॉर्ड अपना 工程部位 और 交底人 बताता है, और उसमें 交底人, 被交底人 तथा 专职安全员 — तीनों हस्ताक्षरों के लिए स्थान है।

## आउटपुट कैसा दिखता है

![Terminal demo of dsh-safety-brief-check: real output over its SB-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-safety-brief-check/main/docs/assets/dsh-safety-brief-check-demo.png)

इस प्लगइन का अपने ही `SB-002` टेस्ट फ़िक्स्चर पर वास्तविक आउटपुट — कोई नकली चित्र नहीं। नियम-पैक उद्धरण नहीं गढ़ता, इसलिए हर निष्कर्ष लागू किए गए खंड का नाम और यह भी बताता है कि उसका मूल पाठ इस बार प्राप्त नहीं हुआ।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| ब्रीफ किए गए लोगों में से एक ने कभी हस्ताक्षर नहीं किया। रिपोर्ट क्या कहती है? | `SB-002` — पैक का एकमात्र `error` स्तर का नियम — 被交底人 की सूची की 签字 की सूची से तुलना करता है और हर उस व्यक्ति को दर्ज करता है जो उसमें नहीं मिलता; हस्ताक्षर सूची में दो बार आया नाम अलग से दर्ज होता है, क्योंकि दोनों कमियों का सुधार अलग-अलग है। यह केवल दोनों सूचियों की तुलना करता है: यह नहीं बता सकता कि हस्ताक्षर उसी व्यक्ति का है, और व्यक्ति-वार हस्ताक्षर की माँग नहीं करता — यदि आपकी संस्था सामूहिक हस्ताक्षर की अनुमति देती है तो सामग्री में वह लिखें या नियम को `disabledRules` में डालें। |
| 交底日期 施工日期 से बाद की है। क्या यह त्रुटि है? | `SB-003` इसे दर्ज करता है; एक ही दिन को बाद की नहीं माना जाता। नियम `warn` तक सीमित है: 第二十七条 में 施工前 केवल समय की पूर्व-शर्त है और वह यह तुलना शब्दशः नहीं कहता, इसलिए यह निष्कर्ष समीक्षा के लिए संकेत है — काम के बीच में बाद में मिले खतरे के लिए जोड़ी गई ब्रीफिंग का बाद की होना सामान्य है और रिकॉर्ड में वह लिखा होना चाहिए। जो तारीख़ पढ़ी न जा सके वह चुपचाप छोड़े जाने के बजाय अलग से दर्ज होती है। |
| जाँच पास होने के लिए रिकॉर्ड में कौन-से कॉलम भरने होंगे? | `SB-001` `requiredFields` पढ़ता है, जो पैक में खाली है, इसलिए यह पास होने के बजाय `skipped` (未配置) दर्ज करता है। अपने फ़ॉर्म के कॉलम देने पर यह हर अनुपस्थित या खाली कॉलम दर्ज करता है — खाली स्ट्रिंग को भरा हुआ नहीं माना जाता — और यह नहीं आँकता कि उसमें लिखा सही है या नहीं। |
| रिकॉर्ड में 被交底人 कॉलम है, पर 专职安全员 के हस्ताक्षर का स्थान नहीं। | `SB-006` हेडर में तीनों पक्षों — 交底人, 被交底人, 专职安全员 — के लिए स्थान की जाँच करता है और जिसका कॉलम न हो उसे दर्ज करता है; कॉलम के नाम आपके फ़ॉर्म के अनुसार बदले जा सकते हैं। यह `warn` पर ही रहता है क्योंकि JGJ 59-2011 का 第3.1.3条 सिफ़ारिशी मूल्यांकन खंड है (मानक के अनिवार्य खंड 第4.0.1、5.0.3条 住房和城乡建设部公告 2022 年第 164 号 द्वारा निरस्त कर दिए गए)। यह देखता है कि स्थान मौजूद है या नहीं, यह नहीं कि किसी ने वहाँ हस्ताक्षर किया — वह `SB-002` का सवाल है। |
| उस हिस्से पर काम करने वाले 工种 ब्रीफिंग की 工种 सूची में नहीं हैं। | `SB-005` काम करने वाले 工种 की रिकॉर्ड की 工种 सूची से तुलना करता है और जो नहीं मिलते उन्हें दर्ज करता है। यह `warn` तक सीमित है क्योंकि JGJ 59-2011 ब्रीफिंग 分部分项 माँगता है पर 工种 के साथ कोई अनिवार्य मानचित्रण नहीं देता; और जब न सामग्री न `workTrades` पैरामीटर काम करने वाले 工种 बताते हैं, तब यह `skipped` दर्ज करता है — यह कोई 工种 सूची कठोरता से नहीं रखता। यह केवल नामों की तुलना करता है, इसलिए 钢筋工 और 钢筋班组 अलग गिने जाते हैं, और यह नहीं आँकता कि ब्रीफिंग की सामग्री उस 工种 को संबोधित करती है या नहीं। |
| रिकॉर्ड में नहीं लिखा कि यह किस 工程部位 के लिए है और ब्रीफिंग किसने दी। | `SB-004` चाहता है कि हेडर 工程部位 (`subject`) और 交底人 (`briefer`) बताए, और जो न हो उसे दर्ज करता है; `requireHeader` false होने पर यह नियम चलता ही नहीं। यह `warn` तक सीमित है क्योंकि GB 50870-2013 का 第8.2.1条 हेडर फ़ील्ड शब्दशः नहीं गिनाता: इनके बिना रिकॉर्ड यह नहीं दिखा सकता कि किसने किसे किस हिस्से की ब्रीफिंग दी, इसलिए यह निष्कर्ष पता-लगाने का संकेत है, यह कथन नहीं कि खंड का उल्लंघन हुआ। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
|---|---|---|
| 《建筑施工安全技术统一规范》 | GB 50870-2013 | SB-001, SB-002, SB-004, SB-007 |
| 《建筑施工安全检查标准》 | JGJ 59-2011 | SB-001, SB-002, SB-005, SB-006, SB-007 |
| 《建设工程安全生产管理条例》 | 国务院令第393号 | SB-002, SB-003 |

**Boundary:** this plugin checks one **安全技术交底记录** for what a record can be held to — that the
columns your form requires are filled, that **everyone briefed appears as having signed**, that the
briefing is dated no later than the work, that the briefed trades cover the trades doing the work, and
that the record identifies its location and briefer. It does **not** judge whether the briefing content
was adequate, whether it was targeted at the right hazards, or whether a signature is genuine.

> ### ⚠️ One `error`, and two annulled mandatory provisions the pack refuses to misuse
>
> **`SB-002` is the only `error`-level rule**, and it rests on an administrative regulation:
> 《建设工程安全生产管理条例》**第二十七条** requires the briefing to be given "并由双方签字确认", with
> 第六十四条第（一）项 as its penalty. Everything else is capped at `warn` or `info`.
>
> The pack records two corrections that a reader would otherwise get wrong:
>
> **1. JGJ 59-2011's clause 3.1.3 — this plugin's closest fit — is a *recommendatory* assessment clause.**
> The standard's only mandatory provisions were 4.0.1 and 5.0.3, and **both were annulled** by
> 住房和城乡建设部公告 2022 年第 164 号 (effective 2023-06-01). So `SB-006` (three-party signatures) is
> `warn`, and its note says why.
>
> **2. GB 50656-2011's clause 10.0.6 lost its mandatory status by the same公告, and its "班前安全操作规程交底"
> wording sits in the 条文说明, not in a clause.** So this pack **does not cite that standard at all** —
> a test asserts the number never appears.
>
> **National law has no provision on pre-shift meetings.** 《安全生产法》's 119 articles contain no
> occurrence of 班前; neither the law, an administrative regulation, a departmental rule nor a national
> standard addresses it. Provincial documents (Shandong's 班前"晨会" guidance, for instance) exist but are
> **local, not national** — so any pre-shift check ships unconfigured and the pack says so.
>
> Stated limits: the signature check **compares name lists only** and cannot tell whether a signature is
> the person's own; the content check is a **literal word-occurrence test** and cannot tell whether a
> briefing was any good — JGJ 59-2011's own scoring table deducts points for "针对性不强", a judgement no
> string operation can make.

## Compatibility

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-safety-brief-check
dsh --profile <name> --dump-config | grep 'dsh-safety-brief-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/safety-brief-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-safety-brief-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-safety-brief-check contributors.
