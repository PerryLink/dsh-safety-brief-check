/**
 * Pure check core: `(input, ruleset, options) => Report`.
 *
 * No plugin context, no I/O, no clock and no model access, so the whole rule set
 * is unit-testable without credentials. Every finding carries the verbatim clause
 * that produced it, and every check that could not run is reported in `skipped`
 * so an empty issue list can never be read as "the record is fine".
 *
 * The checks are about the record's **completeness and closure**: does everyone
 * who was briefed appear as having signed, is the briefing dated before the work,
 * does the trade list match the work. Whether the briefing content was adequate is
 * the briefing engineer's judgement and nothing here attempts it.
 */

import { disabledAsSkipped, formatBasis } from './shared/rules.ts'
import { paramStrings, ruleById } from './shared/ruleset.ts'
import { issueId, makeReport } from './shared/report.ts'
import { parseWallClock } from './shared/datetime.ts'
import type { Issue, Locator, Report, Skipped } from './shared/report.ts'
import type { Ruleset } from './shared/rules.ts'
import type { BriefInput } from './model.ts'

/** Options that come from the plugin configuration rather than the rule pack. */
export interface CheckOptions {
  plugin: string
  checkedAt: string
  disabledRules: readonly string[]
  onlyRules: readonly string[]
  /** Trades the project actually uses, when the deployment wants them compared. */
  workTrades?: readonly string[]
  skipNotes?: string
}

interface RuleContext {
  input: BriefInput
  ruleset: Ruleset
  issues: Issue[]
  skipped: Skipped[]
  fired: Set<string>
  skipReasons: Map<string, string>
  options: CheckOptions
  add(ruleId: string, locator: Locator, found: string, expected: string, fix?: string): void
  skip(ruleId: string, reason: string): void
}

function makeAdd(context: Omit<RuleContext, 'add' | 'skip'>): RuleContext['add'] {
  return (ruleId, locator, found, expected, fix) => {
    const rule = ruleById(context.ruleset, ruleId)
    const issue: Issue = {
      id: issueId(context.ruleset.plugin, ruleId, locator),
      ruleId,
      severity: rule.severity,
      locator,
      found,
      expected,
      basis: formatBasis(rule.basis, rule.alsoBasis ?? []),
    }
    if (fix !== undefined) issue.fix = fix
    context.issues.push(issue)
    context.fired.add(ruleId)
  }
}

/** The comparable form of a person's or trade's name. */
function nameKey(name: string): string {
  return name.replace(/[\s\u3000]/g, '')
}

/** SB-001 — the record carries the fields the deployment requires. */
function checkRequiredFields(context: RuleContext): void {
  const ruleId = 'SB-001'
  const rule = ruleById(context.ruleset, ruleId)
  const required = paramStrings(rule, 'requiredFields', [])
  if (required.length === 0) {
    context.skip(
      ruleId,
      '规则库未配置 requiredFields：交底记录的栏目清单随所用表式与本机构制度变化，本插件不硬编码',
    )
    return
  }
  const missing = required.filter((field) => {
    const value = context.input.fields[field]
    return value === undefined || value.trim() === ''
  })
  if (missing.length === 0) return
  context.add(
    ruleId,
    {},
    `交底记录缺少 ${missing.length} 个栏目：${missing.join('、')}`,
    `按本机构配置，交底记录应填写 ${required.join('、')}`,
    '补齐栏目；本条只核对是否填写，不判断填写内容是否正确',
  )
}

/**
 * SB-002 — everyone briefed appears among the signers.
 *
 * The signature is the evidence that a briefing happened, so an unsigned
 * recipient is the one gap a checker can find mechanically. A repeated signature
 * is reported separately from a missing one, because the two need different fixes.
 */
function checkSignatureClosure(context: RuleContext): void {
  const ruleId = 'SB-002'
  if (context.input.recipients.length === 0 || context.input.signers.length === 0) {
    context.skip(ruleId, '材料没有同时提供被交底人与签字两列（或至少一列为空），无法核对签字闭环')
    return
  }
  const signed = new Map<string, number>()
  for (const signer of context.input.signers) {
    const key = nameKey(signer.name)
    signed.set(key, (signed.get(key) ?? 0) + 1)
  }
  for (const person of context.input.recipients) {
    if (signed.has(nameKey(person.name))) continue
    context.add(
      ruleId,
      { row: person.row ?? 0, column: '被交底人' },
      `被交底人「${person.name}」在签字列表中未出现`,
      '被交底人应当在交底记录上签字确认',
      '核对是否漏签；本条只比对名单，不判断签字是否为本人所签',
    )
  }
  for (const [key, count] of signed) {
    if (count <= 1) continue
    const first = context.input.signers.find((signer) => nameKey(signer.name) === key)
    context.add(
      ruleId,
      { row: first?.row ?? 0, column: '签字' },
      `签字列表中「${first?.name ?? key}」出现 ${count} 次`,
      '同一人不应在签字列表中重复出现',
      '核对是否重复登记；本条不判断签字是否有效',
    )
  }
}

/** SB-003 — the briefing happened before the work. */
function checkChronology(context: RuleContext): void {
  const ruleId = 'SB-003'
  const briefed = parseWallClock(context.input.briefedAt ?? '')
  const work = parseWallClock(context.input.workStartAt ?? '')
  const unreadable: { column: string; raw: string | undefined }[] = []
  if (context.input.briefedAt !== undefined && briefed === undefined) {
    unreadable.push({ column: '交底日期', raw: context.input.briefedAt })
  }
  if (context.input.workStartAt !== undefined && work === undefined) {
    unreadable.push({ column: '施工日期', raw: context.input.workStartAt })
  }
  for (const entry of unreadable) {
    context.add(
      ruleId,
      { column: entry.column },
      `${entry.column}「${entry.raw}」无法解析为日期`,
      '日期应写成可解析的形式，如 2026-03-15',
      '按本机构统一的日期写法填写；无法解析时先后核对不成立',
    )
  }
  if (unreadable.length > 0) return
  if (briefed === undefined || work === undefined) {
    context.skip(ruleId, '材料缺少交底日期或施工日期，无法核对先后')
    return
  }
  if (briefed.date <= work.date) return
  context.add(
    ruleId,
    { column: '交底日期' },
    `交底日期 ${briefed.date} 晚于施工日期 ${work.date}`,
    '安全技术交底应在作业开始前完成',
    '核对两个日期的填写；若确为作业中途补充交底，应在记录中说明',
  )
}

/** SB-004 — the briefed trades line up with the trades that will do the work. */
function checkTradeCoverage(context: RuleContext): void {
  const ruleId = 'SB-004'
  const rule = ruleById(context.ruleset, ruleId)
  const actual = [...(context.options.workTrades ?? []), ...context.input.workTrades]
  if (context.input.trades.length === 0) {
    context.skip(ruleId, '材料没有可识别的被交底工种列，无法核对工种覆盖')
    return
  }
  if (actual.length === 0) {
    context.skip(ruleId, '材料与配置均未提供实际参建工种（workTrades）：工种清单因工程而异，本插件不硬编码')
    return
  }
  if (rule.params.requireTradeMatch === false) {
    context.skip(ruleId, '规则库配置为不要求工种一致，本条不执行')
    return
  }
  const briefedKeys = new Set(context.input.trades.map(nameKey))
  const uncovered = actual.filter((trade) => !briefedKeys.has(nameKey(trade)))
  if (uncovered.length === 0) return
  context.add(
    ruleId,
    { column: '工种' },
    `实际参建工种中有 ${uncovered.length} 个未出现在交底记录的工种列表中：${uncovered.join('、')}`,
    '各参建工种均应在作业前接受安全技术交底',
    '核对是否漏交底或工种名称写法不一致；本条只比对名称，不判断交底内容是否覆盖该工种',
  )
}

/** SB-005 — the record can be identified. */
function checkHeader(context: RuleContext): void {
  const ruleId = 'SB-005'
  const rule = ruleById(context.ruleset, ruleId)
  if (rule.params.requireHeader === false) {
    context.skip(ruleId, '规则库配置为不要求交底记录表头，本条不执行')
    return
  }
  const missing: string[] = []
  if (context.input.project === undefined) missing.push('工程/部位名称')
  if (context.input.briefer === undefined) missing.push('交底人')
  if (missing.length === 0) return
  context.add(
    ruleId,
    {},
    `交底记录缺少 ${missing.join('、')}`,
    '交底记录应能识别交底的工程部位与交底人',
    '补填表头字段',
  )
}

/**
 * SB-003 — the record leaves room for all three signatures the standard names.
 *
 * JGJ 59-2011 requires the 交底人, the 被交底人 **and** the 专职安全员 to sign. This
 * check looks at whether the record carries a place for each of the three, which
 * is a different question from SB-002's "did every recipient actually sign".
 */
function checkThreePartySignatures(context: RuleContext): void {
  const ruleId = 'SB-006'
  const rule = ruleById(context.ruleset, ruleId)
  // The rule pack declares the parties under both `parties` and `check.fields`;
  // read whichever the deployment's pack actually carries.
  const declared = paramStrings(rule, 'parties', [])
  const check = rule.params.check
  const fromCheck =
    typeof check === 'object' && check !== null && Array.isArray((check as Record<string, unknown>).fields)
      ? ((check as Record<string, unknown>).fields as unknown[]).filter((entry): entry is string => typeof entry === 'string')
      : []
  const required = declared.length > 0 ? declared : fromCheck.length > 0 ? fromCheck : ['交底人', '被交底人', '专职安全员']
  const present = new Set(Object.keys(context.input.fields))
  const missing = required.filter((party) => {
    // A party counts as provided when its own column exists, or when a column
    // starting with its name does (forms write `工作负责人签名`).
    if (present.has(party)) return false
    for (const key of present) if (key.startsWith(party)) return false
    return true
  })
  if (missing.length === 0) return
  context.add(
    ruleId,
    {},
    `交底记录没有 ${missing.join('、')} 的签字位置`,
    '安全技术交底应由交底人、被交底人、专职安全员进行签字确认',
    '补齐签字栏；本条只核对位置是否齐备，不判断签字是否有效。JGJ 59-2011 第3.1.3条属推荐性检查评定条款，故本条为提示级',
  )
}

/**
 * SB-007 — the briefing text touches the themes the standard enumerates.
 *
 * A literal-occurrence check only: the words appearing does not mean the briefing
 * was any good, which is why the rule stays at `warn` and its note quotes the
 * scoring table that deducts points for a briefing that is not targeted.
 */
function checkContentThemes(context: RuleContext): void {
  const ruleId = 'SB-007'
  const rule = ruleById(context.ruleset, ruleId)
  const terms = paramStrings(rule, 'terms', [])
  const columns = paramStrings(rule, 'contentColumns', [])
  if (terms.length === 0) {
    context.skip(ruleId, '规则库未配置 terms，本条不执行')
    return
  }
  const scope = columns.length > 0 ? columns : Object.keys(context.input.fields)
  const text = scope.map((column) => context.input.fields[column] ?? '').join('\n')
  if (text.trim() === '') {
    context.skip(ruleId, `材料中没有可读取交底内容的栏目（已按 ${scope.join(' / ')} 查找），无法核对`)
    return
  }
  const missing = terms.filter((term) => !text.includes(term))
  if (missing.length === 0) return
  context.add(
    ruleId,
    { column: columns[0] ?? '交底内容' },
    `交底内容中未出现 ${missing.length} 项：${missing.join('、')}`,
    '安全技术交底应结合施工作业场所状况、特点、工序，对危险因素、施工方案、规范标准、操作规程和应急措施进行交底',
    '核对交底内容是否涵盖；本条只做字面出现性核对，不判断内容是否充分',
  )
}

const CHECKERS: readonly ((context: RuleContext) => void)[] = [
  checkRequiredFields,
  checkSignatureClosure,
  checkChronology,
  checkTradeCoverage,
  checkHeader,
  checkThreePartySignatures,
  checkContentThemes,
]

/**
 * Run the whole rule pack against one briefing record.
 * @param input - normalized record.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value and rule selection.
 * @returns the report, with `skipped` listing every check that did not run.
 */
export function runCheck(input: BriefInput, ruleset: Ruleset, options: CheckOptions): Report {
  const disabled = new Set([...ruleset.disabled, ...options.disabledRules])
  const only = new Set(options.onlyRules)
  const base = {
    input,
    ruleset,
    issues: [] as Issue[],
    skipped: [] as Skipped[],
    fired: new Set<string>(),
    skipReasons: new Map<string, string>(),
    options,
  }
  const context: RuleContext = {
    ...base,
    add: makeAdd(base),
    skip: (ruleId, reason) => {
      base.skipReasons.set(ruleId, reason)
    },
  }

  for (const checker of CHECKERS) checker(context)

  const withNote = (reason: string): string => (options.skipNotes === undefined ? reason : `${reason}；${options.skipNotes}`)
  const skipped: Skipped[] = disabledAsSkipped(ruleset, [...disabled], withNote('该规则在当前配置中被禁用'))
  const already = new Set(skipped.map((entry) => entry.rule))
  for (const [ruleId, reason] of base.skipReasons) {
    if (already.has(ruleId)) continue
    if (disabled.has(ruleId) || (options.onlyRules.length > 0 && !only.has(ruleId))) continue
    skipped.push({ rule: ruleId, reason: withNote(reason) })
    already.add(ruleId)
  }
  for (const rule of ruleset.rules) {
    if (disabled.has(rule.id) || base.fired.has(rule.id) || already.has(rule.id)) continue
    if (options.onlyRules.length > 0 && !only.has(rule.id)) continue
    skipped.push({ rule: rule.id, reason: withNote('材料满足该检查的前置条件且未发现差异条目') })
  }
  if (options.onlyRules.length > 0) {
    const notSelected = ruleset.rules.filter((rule) => !only.has(rule.id) && !disabled.has(rule.id))
    if (notSelected.length > 0) {
      skipped.push({
        rule: notSelected.map((rule) => rule.id).join(','),
        reason: withNote(`本次调用通过 only 参数把执行范围限制为 ${[...only].join(', ')}，上列规则未执行`),
      })
    }
  }

  return makeReport({
    plugin: options.plugin,
    target: input.target,
    rulesetVersion: ruleset.version,
    checkedAt: options.checkedAt,
    issues: context.issues,
    skipped,
  })
}
