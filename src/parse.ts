/**
 * Reader for the safety-briefing record.
 *
 * The material is JSON or YAML: a flat mapping of the record's own field names,
 * plus either a `recipients`/`signers` list or a delimited string such as
 * `张三、李四、王五`.
 */

import { YamlSubsetError, parseYaml } from './shared/yaml.ts'
import { COLUMNS, splitNames } from './model.ts'
import type { BriefInput, Person } from './model.ts'

/** Raised when the material cannot be read at all. */
export class MaterialError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'MaterialError'
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function text(value: unknown): string | undefined {
  if (value === undefined || value === null) return undefined
  if (typeof value === 'string') return value.trim() === '' ? undefined : value.trim()
  if (typeof value === 'number' && Number.isFinite(value)) return String(value)
  return undefined
}

/** Read a person list from either an array or a delimited string. */
function readPeople(value: unknown, where: string): Person[] {
  if (value === undefined || value === null) return []
  if (typeof value === 'string') {
    return splitNames(value).map((name) => ({ name }))
  }
  if (!Array.isArray(value)) throw new MaterialError(`${where} 必须是列表或分隔字符串`)
  const out: Person[] = []
  value.forEach((entry, index) => {
    if (typeof entry === 'string') {
      const name = text(entry)
      if (name !== undefined) out.push({ name, row: index + 1 })
      return
    }
    if (!isRecord(entry)) throw new MaterialError(`${where}[${index}] 必须是字符串或映射`)
    const name = text(entry.name ?? entry.姓名 ?? entry.人员)
    if (name === undefined) throw new MaterialError(`${where}[${index}] 缺少 name 字段`)
    const person: Person = { name, row: index + 1 }
    out.push(person)
  })
  return out
}

/** Read a trade list from either an array or a delimited string. */
function readTrades(value: unknown): string[] {
  if (value === undefined || value === null) return []
  if (typeof value === 'string') return splitNames(value)
  if (!Array.isArray(value)) return []
  return value
    .map((entry) => text(entry))
    .filter((entry): entry is string => entry !== undefined)
}

/** Find the first present value among a set of candidate column names. */
function pick(fields: Record<string, string>, names: readonly string[]): string | undefined {
  const normalize = (value: string): string => value.toLowerCase().replace(/[\s\u3000_-]/g, '')
  for (const name of names) {
    const direct = fields[name]
    if (direct !== undefined && direct !== '') return direct
    const loose = Object.keys(fields).find((key) => normalize(key) === normalize(name))
    if (loose !== undefined) {
      const value = fields[loose]
      if (value !== undefined && value !== '') return value
    }
  }
  return undefined
}

/** Find a person/trade list that may arrive either as a top-level field or as a row column. */
function pickList(document: Record<string, unknown>, fields: Record<string, string>, names: readonly string[]): unknown {
  for (const name of names) {
    if (document[name] !== undefined && document[name] !== null) return document[name]
  }
  return pick(fields, names)
}

/**
 * Parse material into the normalized input contract.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized input.
 */
export function parseMaterial(source: string, target: string): BriefInput {
  const trimmed = source.trim()
  if (trimmed === '') throw new MaterialError('材料为空')
  let document: unknown
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    try {
      document = JSON.parse(trimmed)
    } catch (error) {
      throw new MaterialError(`JSON 无法解析：${error instanceof Error ? error.message : String(error)}`)
    }
  } else {
    try {
      document = parseYaml(trimmed)
    } catch (error) {
      if (error instanceof YamlSubsetError) throw new MaterialError(`YAML 无法解析：${error.message}`)
      throw error
    }
  }
  if (!isRecord(document)) throw new MaterialError('材料根节点必须是映射（一份交底记录）')

  const fields: Record<string, string> = {}
  for (const [key, value] of Object.entries(document)) {
    if (value === undefined || value === null) continue
    if (isRecord(value) || Array.isArray(value)) continue
    const rendered = text(value)
    if (rendered !== undefined) fields[key] = rendered
  }

  const input: BriefInput = {
    target,
    recipients: readPeople(pickList(document, fields, COLUMNS.recipients), 'recipients'),
    signers: readPeople(pickList(document, fields, COLUMNS.signers), 'signers'),
    trades: readTrades(pickList(document, fields, COLUMNS.trades)),
    workTrades: readTrades(pickList(document, fields, COLUMNS.workTrades)),
    fields,
    warnings: [],
  }

  const project = pick(fields, COLUMNS.project)
  if (project !== undefined) input.project = project
  const briefedAt = pick(fields, COLUMNS.briefedAt)
  if (briefedAt !== undefined) input.briefedAt = briefedAt
  const workStartAt = pick(fields, COLUMNS.workStartAt)
  if (workStartAt !== undefined) input.workStartAt = workStartAt
  const briefer = pick(fields, COLUMNS.briefer)
  if (briefer !== undefined) input.briefer = briefer

  if (Object.keys(fields).length === 0 && input.recipients.length === 0 && input.signers.length === 0) {
    throw new MaterialError('材料中没有任何可读字段，无法执行检查')
  }
  if (input.recipients.length === 0) {
    input.warnings.push('材料没有可识别的被交底人，签字闭环相关的检查将无法执行')
  }
  if (input.signers.length === 0) {
    input.warnings.push('材料没有可识别的签字列，签字闭环相关的检查将无法执行')
  }
  return input
}
