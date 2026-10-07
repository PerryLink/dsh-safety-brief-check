/**
 * Input contract for the safety-briefing record checker.
 *
 * The material is one 安全技术交底记录: the briefing's header, the people who must
 * sign it, and the trades it covers. The checker verifies that the record is
 * complete and internally consistent — it never judges whether the briefing
 * content was adequate for the work, which is the briefing engineer's job.
 */

/** One person named on the record. */
export interface Person {
  /** Name exactly as written. */
  name: string
  /** 1-based row, when the names came from a list. */
  row?: number
}

/** The whole normalized input. */
export interface BriefInput {
  target: string
  /** 工程/部位名称. */
  project?: string
  /** 交底日期. */
  briefedAt?: string
  /** 计划/实际开始施工日期. */
  workStartAt?: string
  /** 交底人. */
  briefer?: string
  /** 被交底人, in order. */
  recipients: Person[]
  /** 已签字人员, in order. */
  signers: Person[]
  /** 被交底工种/班组, in order. */
  trades: string[]
  /** 实际参建工种/班组, in order. */
  workTrades: string[]
  /** Values keyed by the record's own column names. */
  fields: Record<string, string>
  warnings: string[]
}

/** Column names recognised as each field, in priority order. */
export const COLUMNS = {
  project: ['工程名称', '单位工程', '分部工程', '工程部位', '部位', 'project'],
  briefedAt: ['交底日期', '交底时间', '日期', 'briefedAt'],
  workStartAt: ['施工日期', '开工日期', '计划开始日期', 'workStartAt'],
  briefer: ['交底人', '交底人签字', '技术交底人', 'briefer'],
  recipients: ['被交底人', '接受交底人', '被交底人员', 'recipients'],
  signers: ['签字', '签名', '已签字人员', 'signers'],
  trades: ['工种', '班组', '被交底工种', 'trades'],
  workTrades: ['参建工种', '实际工种', '涉及工种', 'workTrades'],
} as const

/** Split a cell that holds several names separated by any common delimiter. */
export function splitNames(raw: string): string[] {
  return raw
    .split(/[、,，;；/\s\u3000]+/)
    .map((part) => part.trim())
    .filter((part) => part !== '')
}
