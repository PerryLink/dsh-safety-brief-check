# dsh-safety-brief-check — 安全技术交底记录要素齐备性与签字闭环核对

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-safety-brief-check` 读取一份安全技术交底记录——表头字段、被交底人与签字两份名单、工种列表——核对这份记录自身的齐备与闭环：本机构表式要求的栏目是否填写、被交底人是否都在签字名单中出现且无人重复签字、交底日期是否不晚于施工日期、实际参建工种是否出现在交底记录的工种列表中、记录是否写明工程部位与交底人、是否留有交底人、被交底人、专职安全员三方签字的位置。

## Install

```sh
dsh plugin --profile <name> add dsh-safety-brief-check
dsh --profile <name> --dump-config | grep 'dsh-safety-brief-check'
```

## 实际输出长什么样

![Terminal demo of dsh-safety-brief-check: real output over its SB-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-safety-brief-check/main/docs/assets/dsh-safety-brief-check-hero.png)

![Animated terminal demo of dsh-safety-brief-check](https://raw.githubusercontent.com/PerryLink/dsh-safety-brief-check/main/docs/assets/dsh-safety-brief-check-demo.gif)

本插件对自己 `SB-002` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文：每条发现都会写明所引条款，以及该条 excerpt 是逐字引文还是原则性推论。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 有一位被交底人始终没有签字，报告会说什么？ | `SB-002`——本插件唯一的 `error` 级规则——把被交底人名单与签字名单逐条比对，凡在签字名单中找不到的人都会报出；同一姓名在签字名单中重复出现则单独报出，因为两种缺口的补正方式不同。它只比对这两份名单：无法判断签名是否为本人所签，也不要求逐人签署——若本机构允许集体签署，请在材料中写明签署方式，或把本条列入 `disabledRules`。 |
| 交底日期晚于施工日期，算不算错？ | `SB-003` 会报出；同一天视为不晚于。本条封顶 `warn`：第二十七条只把「施工前」作为时间前提，并未逐字规定这一先后比较，所以它提示的是人工复核线索——作业中途为新发现的危险源补充交底，晚于施工日期是正常的，记录中应加以说明。日期无法解析时会单独报出，不会静默跳过。 |
| 要填哪些栏目才算通过？ | `SB-001` 读取 `requiredFields`，出厂为空，因此它报 `skipped`（未配置），而不是通过。把你表式的栏目列进去之后，它会报出缺失或为空的栏目——空串视为未填——但不判断填写内容是否正确。 |
| 记录里有被交底人栏，却没有专职安全员签字的位置。 | `SB-006` 在表头层面核对三方——交底人、被交底人、专职安全员——是否都有位置，缺哪一栏就报哪一栏；栏位名可按本机构表式替换。本条封顶 `warn`，因为 JGJ 59-2011 第3.1.3条属推荐性检查评定条款（该标准的强制性条文第4.0.1、5.0.3条已被住房和城乡建设部公告 2022 年第 164 号废止）。它只核对位置是否齐备，不判断是否有人签了字——那是 `SB-002` 的问题。 |
| 在该部位作业的工种没有出现在交底记录的工种列表里。 | `SB-004` 把实际参建工种与记录中的工种列表比对，报出未出现的工种。本条封顶 `warn`：JGJ 59-2011 要求交底「分部分项进行」，但未规定交底内容与工种的强制映射表；当材料与 `workTrades` 参数都未提供实际参建工种时，本条报 `skipped`，不硬编码任何工种表。它只比对名称，像「钢筋工」与「钢筋班组」会被算作不同，也不判断交底内容是否针对该工种。 |
| 记录里既没写工程部位，也没写交底人。 | `SB-005` 要求表头能识别工程部位（`subject`）与交底人（`briefer`），缺哪个报哪个；`requireHeader` 为 false 时本条不执行。本条封顶 `warn`，因为 GB 50870-2013 第8.2.1条并未逐字规定表头字段：没有这两项，记录无法确认「谁向谁交了什么部位的底」，所以它提示的是可追溯性线索，而不是认定该条被违反。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 《建筑施工安全技术统一规范》 | GB 50870-2013 | SB-001, SB-002, SB-005, SB-007 |
| 《建筑施工安全检查标准》 | JGJ 59-2011 | SB-001, SB-002, SB-004, SB-006, SB-007 |
| 《建设工程安全生产管理条例》 | 国务院令第393号 | SB-002, SB-003 |

**边界（中文译文，以英文原文为准）：** 本插件核对一份 **安全技术交底记录** 在记录层面可以要求到的内容——你的表单所要求的栏目是否填写，**每一位被交底人是否都显示为已签字**，交底日期是否不晚于作业日期，被交底工种是否覆盖实际作业的工种，以及记录是否写明其地点与交底人。它**不**判定交底内容是否充分、交底是否针对了正确的危险源，或签字是否真实。

> ### ⚠️ 一条 `error`，以及两项已废止的强制性条文——本规则库拒绝误用它们（以英文原文为准）
>
> **`SB-002` 是唯一一条 `error` 级规则**，它依据的是一部行政法规：《建设工程安全生产管理条例》**第二十七条**要求交底「并由双方签字确认」，并以第六十四条第（一）项作为罚则。其余规则的严重级上限都是 `warn` 或 `info`。
>
> 规则库记录了两处更正，否则读者容易弄错：
>
> **1. JGJ 59-2011 第 3.1.3 条——与本插件最贴近的条款——是一条*推荐性*的检查评定条款。** 该标准原本仅有 4.0.1 与 5.0.3 两条强制性条文，而**两条均已被废止**：住房和城乡建设部公告 2022 年第 164 号（2023-06-01 起施行）。因此 `SB-006`（三方签字）为 `warn`，其 note 写明了原因。
>
> **2. GB 50656-2011 第 10.0.6 条因同一份公告失去强制性效力，且其「班前安全操作规程交底」的表述位于条文说明，而不在条文之中。** 因此本规则库**完全不引用该标准**——有测试断言该标准编号从不出现在库中。
>
> **国家法律对班前会没有任何规定。**《安全生产法》共 119 条，其中没有出现「班前」二字；无论是该法、行政法规、部门规章还是国家标准，都没有涉及此事。省级文件（例如山东的班前「晨会」指引）确实存在，但属于**地方性文件，不是国家规定**——因此任何班前检查出厂时都未配置，规则库对此如实说明。
>
> 已写明的局限：签字核对**只比较姓名清单**，无法判断签字是否出自本人；内容核对是**字面词出现与否的检测**，无法判断一次交底做得好不好——JGJ 59-2011 自己的评分表会对「针对性不强」扣分，而这是任何字符串操作都做不出的判断。

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-rc.2`。**已声明 `engines.dsh`**：0.2.1 起由宿主单独裁决，范围为 `>=0.2.1-0 <0.3.0` |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/safety-brief-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-safety-brief-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## PerryLink DSH 插件家族

本项目是 [PerryLink](https://github.com/PerryLink) 维护的 DeepSeek Harness 插件家族成员。完整名单默认折叠，避免每个 README 的首屏被长表淹没；点击展开可查看每一行及其状态。

<details>
<summary>展开全部插件</summary>

| 插件 | 状态 |
|---|---|
| **[dsh-aqua-input-check](https://github.com/PerryLink/dsh-aqua-input-check)** |  |
| **[dsh-archive-check](https://github.com/PerryLink/dsh-archive-check)** |  |
| **[dsh-auto-review](https://github.com/PerryLink/dsh-auto-review)** |  |
| **[dsh-autotier](https://github.com/PerryLink/dsh-autotier)** |  |
| **[dsh-bid-ca-precheck](https://github.com/PerryLink/dsh-bid-ca-precheck)** |  |
| **[dsh-bid-qual-check](https://github.com/PerryLink/dsh-bid-qual-check)** |  |
| **[dsh-cert-mcp](https://github.com/PerryLink/dsh-cert-mcp)** |  |
| **[dsh-checkpoint-rewind](https://github.com/PerryLink/dsh-checkpoint-rewind)** |  |
| **[dsh-click](https://github.com/PerryLink/dsh-click)** |  |
| **[dsh-composer-history](https://github.com/PerryLink/dsh-composer-history)** |  |
| **[dsh-contract-stance](https://github.com/PerryLink/dsh-contract-stance)** |  |
| **[dsh-customs-doc-check](https://github.com/PerryLink/dsh-customs-doc-check)** |  |
| **[dsh-data-quality](https://github.com/PerryLink/dsh-data-quality)** |  |
| **[dsh-demurrage-ledger](https://github.com/PerryLink/dsh-demurrage-ledger)** |  |
| **[dsh-doublecheck](https://github.com/PerryLink/dsh-doublecheck)** |  |
| **[dsh-drill-script-check](https://github.com/PerryLink/dsh-drill-script-check)** |  |
| **[dsh-eia-guide-check](https://github.com/PerryLink/dsh-eia-guide-check)** |  |
| **[dsh-emergency-plan](https://github.com/PerryLink/dsh-emergency-plan)** |  |
| **[dsh-essay-rubric-check](https://github.com/PerryLink/dsh-essay-rubric-check)** |  |
| **[dsh-evidence-check](https://github.com/PerryLink/dsh-evidence-check)** |  |
| **[dsh-export-ctl-check](https://github.com/PerryLink/dsh-export-ctl-check)** |  |
| **[dsh-fast](https://github.com/PerryLink/dsh-fast)** |  |
| **[dsh-fmea-table-check](https://github.com/PerryLink/dsh-fmea-table-check)** |  |
| **[dsh-forecast-penalty](https://github.com/PerryLink/dsh-forecast-penalty)** |  |
| **[dsh-fund-research](https://github.com/PerryLink/dsh-fund-research)** |  |
| **[dsh-github](https://github.com/PerryLink/dsh-github)** |  |
| **[dsh-gongwen-flow-check](https://github.com/PerryLink/dsh-gongwen-flow-check)** |  |
| **[dsh-gongwen-word-check](https://github.com/PerryLink/dsh-gongwen-word-check)** |  |
| **[dsh-guard-plan-qc](https://github.com/PerryLink/dsh-guard-plan-qc)** |  |
| **[dsh-hazchem-check](https://github.com/PerryLink/dsh-hazchem-check)** |  |
| **[dsh-hazplan-check](https://github.com/PerryLink/dsh-hazplan-check)** |  |
| **[dsh-hidden-risk-map](https://github.com/PerryLink/dsh-hidden-risk-map)** |  |
| **[dsh-hs-classify](https://github.com/PerryLink/dsh-hs-classify)** |  |
| **[dsh-icd-rule-check](https://github.com/PerryLink/dsh-icd-rule-check)** |  |
| **[dsh-industry-research](https://github.com/PerryLink/dsh-industry-research)** |  |
| **[dsh-lawcite-adapter](https://github.com/PerryLink/dsh-lawcite-adapter)** |  |
| **[dsh-laya](https://github.com/PerryLink/dsh-laya)** |  |
| **[dsh-lc-doc-check](https://github.com/PerryLink/dsh-lc-doc-check)** |  |
| **[dsh-learning-gap-check](https://github.com/PerryLink/dsh-learning-gap-check)** |  |
| **[dsh-library](https://github.com/PerryLink/dsh-library)** |  |
| **[dsh-local-ai](https://github.com/PerryLink/dsh-local-ai)** |  |
| **[dsh-lsp-actions](https://github.com/PerryLink/dsh-lsp-actions)** |  |
| **[dsh-mask](https://github.com/PerryLink/dsh-mask)** |  |
| **[dsh-mcp-panel](https://github.com/PerryLink/dsh-mcp-panel)** |  |
| **[dsh-medrec-qc](https://github.com/PerryLink/dsh-medrec-qc)** |  |
| **[dsh-memento](https://github.com/PerryLink/dsh-memento)** |  |
| **[dsh-nsfc-form-check](https://github.com/PerryLink/dsh-nsfc-form-check)** |  |
| **[dsh-nurse-record-check](https://github.com/PerryLink/dsh-nurse-record-check)** |  |
| **[dsh-observe](https://github.com/PerryLink/dsh-observe)** |  |
| **[dsh-origin-rvc-check](https://github.com/PerryLink/dsh-origin-rvc-check)** |  |
| **[dsh-ota-review-check](https://github.com/PerryLink/dsh-ota-review-check)** |  |
| **[dsh-output-styles](https://github.com/PerryLink/dsh-output-styles)** |  |
| **[dsh-paper-doc-adapter](https://github.com/PerryLink/dsh-paper-doc-adapter)** |  |
| **[dsh-permission-rules](https://github.com/PerryLink/dsh-permission-rules)** |  |
| **[dsh-permit-report-check](https://github.com/PerryLink/dsh-permit-report-check)** |  |
| **[dsh-pipeline-check](https://github.com/PerryLink/dsh-pipeline-check)** |  |
| **[dsh-pleading-draft](https://github.com/PerryLink/dsh-pleading-draft)** |  |
| **[dsh-plugin-doctor](https://github.com/PerryLink/dsh-plugin-doctor)** |  |
| **[dsh-plugin-guide](https://github.com/PerryLink/dsh-plugin-guide)** |  |
| **[dsh-plugin-kit](https://github.com/PerryLink/dsh-plugin-kit)** |  |
| **[dsh-plugin-upgrade](https://github.com/PerryLink/dsh-plugin-upgrade)** |  |
| **[dsh-policy-brief-draft](https://github.com/PerryLink/dsh-policy-brief-draft)** |  |
| **[dsh-power-loss-split](https://github.com/PerryLink/dsh-power-loss-split)** |  |
| **[dsh-power-ticket-check](https://github.com/PerryLink/dsh-power-ticket-check)** |  |
| **[dsh-ppap-check](https://github.com/PerryLink/dsh-ppap-check)** |  |
| **[dsh-protest-deadline](https://github.com/PerryLink/dsh-protest-deadline)** |  |
| **[dsh-railway-window](https://github.com/PerryLink/dsh-railway-window)** |  |
| **[dsh-repair-order-qc](https://github.com/PerryLink/dsh-repair-order-qc)** |  |
| **[dsh-research-report](https://github.com/PerryLink/dsh-research-report)** |  |
| **[dsh-review-reply-check](https://github.com/PerryLink/dsh-review-reply-check)** |  |
| **[dsh-rulefile-check](https://github.com/PerryLink/dsh-rulefile-check)** |  |
| **[dsh-safety-brief-check](https://github.com/PerryLink/dsh-safety-brief-check)** |  |
| **[dsh-score](https://github.com/PerryLink/dsh-score)** |  |
| **[dsh-session-sync](https://github.com/PerryLink/dsh-session-sync)** |  |
| **[dsh-site-log-check](https://github.com/PerryLink/dsh-site-log-check)** |  |
| **[dsh-skill-pack-security](https://github.com/PerryLink/dsh-skill-pack-security)** |  |
| **[dsh-soe-decision-check](https://github.com/PerryLink/dsh-soe-decision-check)** |  |
| **[dsh-soilwater-check](https://github.com/PerryLink/dsh-soilwater-check)** |  |
| **[dsh-sop-sync-check](https://github.com/PerryLink/dsh-sop-sync-check)** |  |
| **[dsh-spc-gbt-adapter](https://github.com/PerryLink/dsh-spc-gbt-adapter)** |  |
| **[dsh-talk](https://github.com/PerryLink/dsh-talk)** |  |
| **[dsh-tender-extract](https://github.com/PerryLink/dsh-tender-extract)** |  |
| **[dsh-tender-matrix](https://github.com/PerryLink/dsh-tender-matrix)** |  |
| **[dsh-test-drive](https://github.com/PerryLink/dsh-test-drive)** |  |
| **[dsh-ticktick](https://github.com/PerryLink/dsh-ticktick)** |  |
| **[dsh-translate](https://github.com/PerryLink/dsh-translate)** |  |
| **[dsh-warranty-calc](https://github.com/PerryLink/dsh-warranty-calc)** |  |
| **[dsh-budget](https://github.com/PerryLink/dsh-budget)** | 🧊 已冻结 — 见仓库 README |
| **[dsh-claude-move](https://github.com/PerryLink/dsh-claude-move)** | 🧊 已冻结 — 见仓库 README |
| **[dsh-defend](https://github.com/PerryLink/dsh-defend)** | 🧊 已冻结 — 见仓库 README |
| **[dsh-draw](https://github.com/PerryLink/dsh-draw)** | 🧊 已冻结 — 见仓库 README |
| **[dsh-reach](https://github.com/PerryLink/dsh-reach)** | 🧊 已冻结 — 见仓库 README |
| **[dsh-background-agents](https://github.com/PerryLink/dsh-background-agents)** | 🚫 已退役 — 见仓库 README |
| **[dsh-session-pin](https://github.com/PerryLink/dsh-session-pin)** | 🚫 已退役 — 见仓库 README |
| **[dsh-team-rooms](https://github.com/PerryLink/dsh-team-rooms)** | 🚫 已退役 — 见仓库 README |

</details>## License

[Apache License 2.0](LICENSE) © 2026 dsh-safety-brief-check contributors.
