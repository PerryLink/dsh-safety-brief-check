import { readFile, readdir } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { loadRuleset } from '../src/shared/ruleset.ts'
import { parseMaterial } from '../src/parse.ts'
import { runCheck } from '../src/check.ts'
import { buildView } from '../src/view.ts'
import { findForbiddenWording } from '../src/shared/wording.ts'
import { addDays, diffDays, parseWallClock } from '../src/shared/datetime.ts'
import { parseYaml } from '../src/shared/yaml.ts'
import { splitNames } from '../src/model.ts'
import { Config as ConfigSchema } from '../src/config.ts'
import { inject, name as pluginName, resolvePackageFile, TOOL_NAME } from '../src/index.ts'
import type { Report } from '../src/shared/report.ts'
import type { CheckOptions } from '../src/check.ts'

const here = dirname(fileURLToPath(import.meta.url))
const packageRoot = resolve(here, '..')
const rulesPath = join(packageRoot, 'rules', 'safety-brief-check.yaml')
const fixturesRoot = join(here, 'fixtures')
const CHECKED_AT = '2026-10-06T00:00:00.000Z'

interface CaseFile {
  ruleId: string
  configure?: Record<string, Record<string, unknown>>
  workTrades?: string[]
  pairs: { name: string; material: string; expect: { ruleId: string; count: number } }[]
}

async function loadPack() {
  return loadRuleset(await readFile(rulesPath, 'utf8'))
}

function runOptions(overrides: Partial<CheckOptions> = {}): CheckOptions {
  return { plugin: pluginName, checkedAt: CHECKED_AT, disabledRules: [], onlyRules: [], ...overrides }
}

function withConfiguration(ruleset: Awaited<ReturnType<typeof loadPack>>, configure: CaseFile['configure']) {
  if (configure === undefined) return ruleset
  return {
    ...ruleset,
    rules: ruleset.rules.map((rule) =>
      configure[rule.id] === undefined ? rule : { ...rule, params: { ...rule.params, ...configure[rule.id] } },
    ),
  }
}

async function runFixture(
  materialText: string,
  target: string,
  configure?: CaseFile['configure'],
  workTrades?: string[],
): Promise<Report> {
  const ruleset = withConfiguration(await loadPack(), configure)
  return runCheck(
    parseMaterial(materialText, target),
    ruleset,
    runOptions(workTrades === undefined ? {} : { workTrades }),
  )
}

function issuesOf(report: Report, ruleId: string) {
  return report.issues.filter((issue) => issue.ruleId === ruleId)
}

async function ruleDirectories(): Promise<string[]> {
  const entries = await readdir(fixturesRoot, { withFileTypes: true })
  return entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort()
}

async function readCases(directory: string): Promise<CaseFile> {
  return JSON.parse(await readFile(join(fixturesRoot, directory, 'cases.json'), 'utf8')) as CaseFile
}

const GOOD = {
  工程名称: '某某厂房工程',
  交底部位: '二层结构',
  交底日期: '2026-03-10',
  施工日期: '2026-03-12',
  交底人: '张工',
  被交底人: '李四、王五',
  签字: '李四、王五',
  工种: '钢筋工',
}

describe('rule pack', () => {
  it('declares a citable basis for every rule', async () => {
    const ruleset = await loadPack()
    expect(ruleset.plugin).toBe(pluginName)
    expect(ruleset.rules.length).toBeGreaterThanOrEqual(5)
    for (const rule of ruleset.rules) {
      expect(rule.basis.document, `${rule.id} document`).not.toBe('')
      expect(rule.basis.clause, `${rule.id} clause`).not.toBe('')
      expect(rule.basis.excerpt.length, `${rule.id} excerpt`).toBeGreaterThanOrEqual(8)
      expect(rule.basis.source, `${rule.id} source`).toMatch(/^https?:\/\//)
      expect(['direct', 'derived-from-principle', 'institutional-configuration']).toContain(rule.basis.kind)
    }
  })

  it('never lets a principle-derived or locally configured check be an error', async () => {
    const ruleset = await loadPack()
    for (const rule of ruleset.rules) {
      if (rule.basis.kind === 'derived-from-principle') expect(rule.severity, rule.id).not.toBe('error')
      if (rule.basis.kind === 'institutional-configuration') expect(rule.severity, rule.id).toBe('info')
    }
  })

  it('cites verbatim clauses from the regulation, the national standard and the industry standard', async () => {
    const ruleset = await loadPack()
    for (const rule of ruleset.rules) {
      expect(rule.basis.excerpt, rule.id).not.toContain('本次未取得')
      expect(rule.basis.excerpt.length, rule.id).toBeGreaterThan(25)
    }
    const numbers = ruleset.rules.flatMap((rule) => [rule.basis.number, ...(rule.alsoBasis ?? []).map((extra) => extra.number)])
    expect(numbers.some((number) => number.includes('国务院令第393号'))).toBe(true)
    expect(numbers.some((number) => number.includes('GB 50870-2013'))).toBe(true)
    expect(numbers.some((number) => number.includes('JGJ 59-2011'))).toBe(true)
  })

  it('reserves error for the administrative regulation, and records why the industry standard is only warn', async () => {
    const ruleset = await loadPack()
    const errors = ruleset.rules.filter((rule) => rule.severity === 'error').map((rule) => rule.id)
    expect(errors).toEqual(['SB-002'])
    const threeParty = ruleset.rules.find((rule) => rule.id === 'SB-006')
    expect(threeParty?.severity).toBe('warn')
    expect(threeParty?.note).toContain('推荐性检查评定条款')
    expect(threeParty?.note).toContain('住建部公告 2022 年第 164 号')
  })

  it('records that the annulled mandatory status is never claimed', async () => {
    const source = await readFile(rulesPath, 'utf8')
    expect(source).toContain('不得再称其为"强制性条文"')
    expect(source).toContain('JGJ 59-2011 的强制性条文只有第4.0.1、5.0.3条')
    // GB 50656-2011 is deliberately not cited at all.
    for (const rule of await loadPack().then((ruleset) => ruleset.rules)) {
      expect(rule.basis.number, rule.id).not.toContain('GB 50656')
    }
  })

  it('states that national law has no clause on pre-shift meetings', async () => {
    const source = await readFile(rulesPath, 'utf8')
    expect(source).toContain('**国家层面无专门明文**')
    expect(source).toContain('属地方规定，非全国通用')
  })

  it('says plainly that it does not judge the adequacy of the briefing content', async () => {
    const source = await readFile(rulesPath, 'utf8')
    expect(source).toContain('**不判断交底内容是否充分、是否有针对性、是否覆盖了该工种的危险源**')
  })

  it('states that it does not verify whether a signature is genuine', async () => {
    const ruleset = await loadPack()
    const signature = ruleset.rules.find((rule) => rule.id === 'SB-002')
    expect(signature?.note).toContain('不判断签字是否为本人所签')
  })

  it('refuses a rule pack that overstates a principle-derived check', () => {
    const overstated = [
      'plugin: probe',
      'version: "0"',
      'rules:',
      '  - id: X-001',
      '    title: probe',
      '    severity: error',
      '    basis:',
      '      document: 《X》',
      '      number: X〔2020〕1号',
      '      clause: 第一条',
      '      excerpt: 这是一个足够长的逐字摘录示例。',
      '      kind: derived-from-principle',
      '      source: https://example.invalid/x',
    ].join('\n')
    expect(() => loadRuleset(overstated)).toThrow(/strongest permitted severity/)
  })
})

describe('paired fixtures', () => {
  it('has both a compliant and a violating sample for every rule', async () => {
    const ruleset = await loadPack()
    const covered = new Set<string>()
    for (const directory of await ruleDirectories()) {
      const cases = await readCases(directory)
      expect(cases.pairs.filter((pair) => pair.expect.count === 0).length, `${directory} compliant sample`).toBeGreaterThanOrEqual(1)
      expect(cases.pairs.filter((pair) => pair.expect.count > 0).length, `${directory} violating sample`).toBeGreaterThanOrEqual(1)
      for (const pair of cases.pairs) {
        const material = await readFile(join(fixturesRoot, directory, pair.material), 'utf8')
        const report = await runFixture(material, pair.material, cases.configure, cases.workTrades)
        const matched = issuesOf(report, cases.ruleId)
        expect(
          matched.length,
          `${directory}/${pair.name} expected ${pair.expect.count} × ${cases.ruleId}, got ${matched.map((issue) => issue.found).join(' | ')}`,
        ).toBe(pair.expect.count)
        covered.add(cases.ruleId)
      }
    }
    for (const rule of ruleset.rules) expect(covered.has(rule.id), `covered ${rule.id}`).toBe(true)
  })

  it('gives every issue a citable basis and a stable id', async () => {
    for (const directory of await ruleDirectories()) {
      const cases = await readCases(directory)
      for (const pair of cases.pairs) {
        const material = await readFile(join(fixturesRoot, directory, pair.material), 'utf8')
        const report = await runFixture(material, pair.material, cases.configure, cases.workTrades)
        for (const issue of report.issues) {
          expect(issue.basis).toContain('「')
          expect(issue.id).toMatch(/^dsh-safety-brief-check\.SB-\d{3}\.[0-9a-f]{8}$/)
          expect(issue.found).not.toBe('')
          expect(issue.expected).not.toBe('')
        }
      }
    }
  })
})

describe('signature closure', () => {
  it('reports a missing signature and a duplicate signature differently', async () => {
    const ruleset = await loadPack()
    const missing = runCheck(
      parseMaterial(JSON.stringify({ ...GOOD, 被交底人: '李四、王五、赵六', 签字: '李四、王五' }), 'inline'),
      ruleset,
      runOptions(),
    )
    expect(issuesOf(missing, 'SB-002')[0]?.found).toContain('未出现')
    const duplicate = runCheck(
      parseMaterial(JSON.stringify({ ...GOOD, 被交底人: '李四、王五', 签字: '李四、李四、王五' }), 'inline'),
      ruleset,
      runOptions(),
    )
    expect(issuesOf(duplicate, 'SB-002')[0]?.found).toContain('出现 2 次')
  })

  it('accepts names given as an array or as a delimited string', () => {
    const fromArray = parseMaterial(JSON.stringify({ ...GOOD, 被交底人: ['李四', '王五'], 签字: ['王五', '李四'] }), 'inline')
    expect(fromArray.recipients.map((person) => person.name)).toEqual(['李四', '王五'])
    const fromString = parseMaterial(JSON.stringify({ ...GOOD, 被交底人: '李四，王五；赵六' }), 'inline')
    expect(fromString.recipients).toHaveLength(3)
  })

  it('splits names on the delimiters a register uses', () => {
    expect(splitNames('李四、王五')).toEqual(['李四', '王五'])
    expect(splitNames('李四, 王五;赵六/钱七')).toEqual(['李四', '王五', '赵六', '钱七'])
    expect(splitNames('  李四\u3000王五 ')).toEqual(['李四', '王五'])
  })

  it('skips when either list is absent rather than reporting every name as missing', async () => {
    const ruleset = await loadPack()
    const report = runCheck(parseMaterial(JSON.stringify({ ...GOOD, 签字: '' }), 'inline'), ruleset, runOptions())
    expect(issuesOf(report, 'SB-002')).toHaveLength(0)
    expect(report.skipped.find((entry) => entry.rule === 'SB-002')?.reason).toContain('无法核对签字闭环')
  })
})

describe('chronology', () => {
  it('accepts a briefing on the same day as the work', async () => {
    const ruleset = await loadPack()
    const report = runCheck(
      parseMaterial(JSON.stringify({ ...GOOD, 交底日期: '2026-03-12', 施工日期: '2026-03-12' }), 'inline'),
      ruleset,
      runOptions(),
    )
    expect(issuesOf(report, 'SB-003')).toHaveLength(0)
  })

  it('reports an unreadable date instead of silently skipping the order check', async () => {
    const ruleset = await loadPack()
    const report = runCheck(
      parseMaterial(JSON.stringify({ ...GOOD, 交底日期: '二〇二六年三月十日' }), 'inline'),
      ruleset,
      runOptions(),
    )
    const issue = issuesOf(report, 'SB-003')[0]
    expect(issue?.found).toContain('无法解析为日期')
    expect(issue?.locator.column).toBe('交底日期')
  })
})

describe('skipped reporting', () => {
  it('admits that the field list is not configured', async () => {
    const report = await runFixture(JSON.stringify(GOOD), 'inline')
    expect(report.skipped.find((entry) => entry.rule === 'SB-001')?.reason).toContain('未配置 requiredFields')
  })

  it('admits that the work-trade list is unavailable', async () => {
    const report = await runFixture(JSON.stringify(GOOD), 'inline')
    expect(report.skipped.find((entry) => entry.rule === 'SB-004')?.reason).toContain('workTrades')
  })

  it('warns when the record carries no recipient list', () => {
    const input = parseMaterial(JSON.stringify({ 工程名称: '甲', 交底人: '张工' }), 'inline')
    expect(input.warnings.join(' ')).toContain('没有可识别的被交底人')
  })

  it('names disabled rules exactly once and appends the configured note', async () => {
    const ruleset = await loadPack()
    const input = parseMaterial(JSON.stringify(GOOD), 'inline')
    const report = runCheck(input, ruleset, runOptions({ disabledRules: ['SB-005'], skipNotes: '本机构表式' }))
    const entries = report.skipped.filter((item) => item.rule === 'SB-005')
    expect(entries).toHaveLength(1)
    expect(entries[0]?.reason).toContain('禁用')
    expect(entries[0]?.reason).toContain('本机构表式')
  })
})

describe('report rendering', () => {
  it('never uses adjudicating wording and always carries the disclaimer', async () => {
    const material = await readFile(join(fixturesRoot, 'SB-002', 'SB-002-unsafe.json'), 'utf8')
    const report = await runFixture(material, 'SB-002-unsafe.json')
    const view = buildView(report)
    expect(findForbiddenWording(view.markdown)).toEqual([])
    expect(view.markdown).toContain('免责声明')
    expect(view.markdown).toContain('未执行的检查')
    expect(JSON.parse(view.reportJson)).toMatchObject({ plugin: pluginName, summary: report.summary })
  })
})

describe('plugin contract', () => {
  it('declares a static inject array covering every service apply touches', () => {
    expect(Array.isArray(inject)).toBe(true)
    expect(inject).toContain('tools')
  })

  it('exposes a Schemastery Config with serializable defaults', () => {
    const resolved = ConfigSchema(null)
    expect(resolved.rulesFile).toBe('rules/safety-brief-check.yaml')
    expect(resolved.disabledRules).toEqual([])
    expect(resolved.timeoutMs).toBeGreaterThan(0)
  })

  it('resolves the packaged rule pack and rejects a missing one', () => {
    expect(resolvePackageFile('rules/safety-brief-check.yaml')).toBe(rulesPath)
    expect(() => resolvePackageFile('rules/does-not-exist.yaml')).toThrow(/未找到/)
  })

  it('names the tool after the package family convention', () => {
    expect(TOOL_NAME).toBe('safety_brief_check')
  })
})

describe('material reader', () => {
  it('rejects empty material instead of reporting an empty result', () => {
    expect(() => parseMaterial('   ', 'inline')).toThrow(/材料为空/)
  })

  it('rejects a person entry with no name', () => {
    expect(() => parseMaterial(JSON.stringify({ 被交底人: [{ 姓名: '' }] }), 'inline')).toThrow(/缺少 name 字段/)
  })
})

describe('shared kit', () => {
  it('parses wall-clock timestamps and rejects impossible dates', () => {
    expect(parseWallClock('2026-03-15')).toEqual({ date: '2026-03-15', time: '00:00', hasTime: false, minutes: 0 })
    expect(parseWallClock('2026-02-30')).toBeUndefined()
  })

  it('does calendar arithmetic', () => {
    expect(addDays('2026-03-31', 1)).toBe('2026-04-01')
    expect(diffDays('2026-03-01', '2026-03-06')).toBe(5)
  })

  it('reads the supported YAML subset and rejects the rest', () => {
    expect(parseYaml('a: 1\nb:\n  - x\n')).toEqual({ a: 1, b: ['x'] })
    expect(() => parseYaml('a: 1\na: 2\n')).toThrow(/duplicate/)
  })
})
