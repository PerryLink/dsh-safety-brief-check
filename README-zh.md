# dsh-safety-brief-check — 安全技术交底记录要素齐备性与签字闭环核对

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-safety-brief-check` 读取一份安全技术交底记录——表头字段、被交底人与签字两份名单、工种列表——核对这份记录自身的齐备与闭环：本机构表式要求的栏目是否填写、被交底人是否都在签字名单中出现且无人重复签字、交底日期是否不晚于施工日期、实际参建工种是否出现在交底记录的工种列表中、记录是否写明工程部位与交底人、是否留有交底人、被交底人、专职安全员三方签字的位置。

## 实际输出长什么样

![Terminal demo of dsh-safety-brief-check: real output over its SB-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-safety-brief-check/main/docs/assets/dsh-safety-brief-check-demo.png)

本插件对自己 `SB-002` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 有一位被交底人始终没有签字，报告会说什么？ | `SB-002`——本插件唯一的 `error` 级规则——把被交底人名单与签字名单逐条比对，凡在签字名单中找不到的人都会报出；同一姓名在签字名单中重复出现则单独报出，因为两种缺口的补正方式不同。它只比对这两份名单：无法判断签名是否为本人所签，也不要求逐人签署——若本机构允许集体签署，请在材料中写明签署方式，或把本条列入 `disabledRules`。 |
| 交底日期晚于施工日期，算不算错？ | `SB-003` 会报出；同一天视为不晚于。本条封顶 `warn`：第二十七条只把「施工前」作为时间前提，并未逐字规定这一先后比较，所以它提示的是人工复核线索——作业中途为新发现的危险源补充交底，晚于施工日期是正常的，记录中应加以说明。日期无法解析时会单独报出，不会静默跳过。 |
| 要填哪些栏目才算通过？ | `SB-001` 读取 `requiredFields`，出厂为空，因此它报 `skipped`（未配置），而不是通过。把你表式的栏目列进去之后，它会报出缺失或为空的栏目——空串视为未填——但不判断填写内容是否正确。 |
| 记录里有被交底人栏，却没有专职安全员签字的位置。 | `SB-006` 在表头层面核对三方——交底人、被交底人、专职安全员——是否都有位置，缺哪一栏就报哪一栏；栏位名可按本机构表式替换。本条封顶 `warn`，因为 JGJ 59-2011 第3.1.3条属推荐性检查评定条款（该标准的强制性条文第4.0.1、5.0.3条已被住房和城乡建设部公告 2022 年第 164 号废止）。它只核对位置是否齐备，不判断是否有人签了字——那是 `SB-002` 的问题。 |
| 在该部位作业的工种没有出现在交底记录的工种列表里。 | `SB-005` 把实际参建工种与记录中的工种列表比对，报出未出现的工种。本条封顶 `warn`：JGJ 59-2011 要求交底「分部分项进行」，但未规定交底内容与工种的强制映射表；当材料与 `workTrades` 参数都未提供实际参建工种时，本条报 `skipped`，不硬编码任何工种表。它只比对名称，像「钢筋工」与「钢筋班组」会被算作不同，也不判断交底内容是否针对该工种。 |
| 记录里既没写工程部位，也没写交底人。 | `SB-004` 要求表头能识别工程部位（`subject`）与交底人（`briefer`），缺哪个报哪个；`requireHeader` 为 false 时本条不执行。本条封顶 `warn`，因为 GB 50870-2013 第8.2.1条并未逐字规定表头字段：没有这两项，记录无法确认「谁向谁交了什么部位的底」，所以它提示的是可追溯性线索，而不是认定该条被违反。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
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

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-safety-brief-check
dsh --profile <name> --dump-config | grep 'dsh-safety-brief-check'
```

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

## License

[Apache License 2.0](LICENSE) © 2026 dsh-safety-brief-check contributors.
