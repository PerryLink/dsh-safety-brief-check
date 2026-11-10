#!/usr/bin/env python3
"""README visuals for dsh-safety-brief-check — drawn from the shipped run.

Outputs (docs/assets/, idempotent overwrite):

  dsh-safety-brief-check-hero-{zh,en}-{light,dark}.webp   1440x576
  dsh-safety-brief-check-flow-v5-{light,dark}.svg         1100x660

Both figures are derived from what this package actually ships:

  * `samples/quickstart/input/SB-001-unsafe.json` — the briefing record drawn in
    the hero is that file, field for field: 工程名称 某某厂房工程 / 交底部位
    二层结构 / 交底日期 2026-03-10 / 施工日期 2026-03-12 / 交底人 "" (an empty
    string, dropped by `text()` in `src/parse.ts`, so `briefer` is undefined) /
    专职安全员 孙工 / 被交底人 李四、王五、赵六 / 签字 李四、王五、赵六 / 工种
    钢筋工、木工 / 交底内容 危险因素…操作规程…应急措施.
  * `samples/quickstart/expected/result.json` — the run the pictures report:
    issueCount 2, summary { error 0, warn 2, info 0 }, skippedCount 5.
  * `src/check.ts` — that run resolves rule by rule as follows, and the flow
    figure draws exactly this: SB-001 skipped (`requiredFields` unset), SB-002 no
    difference (three recipients, three signers, no duplicate), SB-003 no
    difference (2026-03-10 <= 2026-03-12), SB-004 skipped (`workTrades` unset in
    material and options), SB-005 issue (`briefer` undefined), SB-006 issue (no
    column named 交底人 or starting with it), SB-007 no difference (危险 /
    操作规程 / 应急 all present in the record's fields). 2 + 5 = the 7 rules.
  * `src/check.ts` tail of `runCheck()` — a rule that produced no issue is still
    pushed into `skipped` with "材料满足该检查的前置条件且未发现差异条目", which
    is why the flow spells `skipped[]` out as `not-run + no-difference`. That is
    the claim this plugin makes loudest: an empty `issues[]` is not a pass.
  * `rules/safety-brief-check.yaml` — pack `2026.2`, rules SB-001..SB-007,
    severities info/warn/warn/warn/warn/warn/error, and the evidence-kind caps:
    `derived-from-principle` <= warn, `institutional-configuration` <= info; only
    `direct` may carry `error`, and only SB-002 does.

Hero: left column is the copy block (kicker / two-line wordmark / two value
lines / one subtitle / one meta line / footer). The right side is this plugin's
own artefact: one 安全技术交底记录 sheet (the material it reads) with the empty
交底人 cell tagged SB-005 / SB-006, the recipient-signature pairs all matched,
and beside it the run result — 2 issues, 5 skipped, reasons included. No number
in the picture is invented.

Flow: grammar = a GATE LADDER between two ledgers, not a row of nodes. The
record is normalised (`parse.ts`: COLUMNS aliases, splitNames, trim) into
`BriefInput`; the seven gates read named fields of that model in pack order and
each exits into exactly one of `issues[]` / `skipped[]`; `makeReport()` merges
both into one report; the reviewer takes it from there. The severity caps and the
not-run / no-difference split close the figure as annotations.

Old single-skin assets (`…-flow.svg`, `…-hero.png`, `…-demo.gif`,
`quickstart.*`) are left on disk so existing external links keep resolving; the
READMEs reference only the new hero and flow-v5 pair.

Every label is measured before it is drawn; a label that would overflow aborts
the run instead of shipping clipped text. The SVG is re-parsed and re-rendered
through headless Chrome as a separate check.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow + Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-safety-brief-check"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")

os.makedirs(OUT, exist_ok=True)

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", ok="#15803d", warn="#b45309", danger="#b3261e",
        pill="#ece7f9", band="#f5f2fb", grid="#e7e4f0", cell="#fbfaff",
        shadow=(43, 35, 80), shadow_alpha=52, glow=34,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", ok="#3fb950", warn="#d9a441", danger="#f0776a",
        pill="#242d42", band="#202839", grid="#2b3348", cell="#1e2534",
        shadow=(0, 0, 0), shadow_alpha=148, glow=46,
    ),
}

FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        panel="#ffffff", card="#ffffff", edge="#e6e2ef",
        band="#f5f2fb", pill="#ece7f9", cell="#fbfaff",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", ok="#15803d", warn="#b45309", danger="#b3261e",
        rule="#e7e4f0", shadow="#2b2440", shadow_op="0.14",
        dot="#cfc8e2", dot_op="0.55",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        panel="#1b2231", card="#1b2231", edge="#2e374b",
        band="#202839", pill="#242d42", cell="#1e2534",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", ok="#3fb950", warn="#d9a441", danger="#f0776a",
        rule="#2b3348", shadow="#000000", shadow_op="0.52",
        dot="#2a3346", dot_op="0.55",
    ),
}

FONT_CSS_SANS = ("'Microsoft YaHei','Segoe UI','PingFang SC',"
                 "'Noto Sans CJK SC',sans-serif")
FONT_CSS_MONO = "Consolas,'Microsoft YaHei',ui-monospace,monospace"

# ---------------------------------------------------------------------------
# fonts + measuring
# ---------------------------------------------------------------------------
_font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def font(size: float, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    key = (kind, int(round(size)))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_FILES[kind], int(round(size)))
    return _font_cache[key]


def measure(content: str, size: float, kind: str = "cjk") -> float:
    return _MEASURE.textlength(content, font=font(size, kind))


def require_w(content: str, size: float, kind: str, max_w: float,
              what: str) -> float:
    got = measure(content, size, kind)
    if got > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {content!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")
    return got


def fit(content: str, kind: str, max_w: float, start: float,
        minimum: float) -> float:
    size = float(start)
    while size > minimum:
        if measure(content, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w:.0f}px at >= {minimum}px: "
                     f"{content!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: float,
              minimum: float) -> float:
    return min(fit(line, kind, max_w, start, minimum) for line in lines)


def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------------------
# raster primitives
# ---------------------------------------------------------------------------
def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(top), hx(bottom)
    for y in range(h):
        t = 0.12 * (y / h) + 0.88 * (y / h) ** 1.3
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: str,
         alpha: int) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgb = hx(color)
    for i in range(10, 0, -1):
        rr = r * i / 10
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=rgb + (int(alpha * (1 - i / 11)),))
    return Image.alpha_composite(img.convert("RGBA"),
                                 layer.filter(ImageFilter.GaussianBlur(26))
                                 ).convert("RGB")


def card(img: Image.Image, box: tuple[int, int, int, int], s: dict,
         radius: int = 20, shadow: int = 24, fill: str | None = None,
         edge: str | None = None) -> Image.Image:
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0 + 2, y0 + max(4, shadow // 2), x1 + 2,
                         y1 + max(5, shadow // 2)],
                        radius=radius, fill=s["shadow"] + (s["shadow_alpha"],))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 layer.filter(ImageFilter.GaussianBlur(shadow / 2)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(edge or s["edge"]), width=2)
    return base.convert("RGB")


def put(img: Image.Image, xy: tuple[float, float], content: str, size: float,
        kind: str, color: str, *, anchor: str = "ls", max_w: float | None = None,
        what: str = "text") -> float:
    got = measure(content, size, kind)
    if max_w is not None and got > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {content!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")
    ImageDraw.Draw(img).text(xy, content, font=font(size, kind),
                             fill=hx(color), anchor=anchor)
    return got


def pill(img: Image.Image, xy: tuple[int, int], content: str, s: dict,
         size: float = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold", height: int | None = None, pad: int = 30) -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(content, font=f)
    x, y = xy
    hh = height if height is not None else int(size) + 20
    d.rounded_rectangle([x, y, x + w + pad, y + hh], radius=hh // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + pad / 2, y + hh / 2), content, font=f,
           fill=hx(fg or s["accent"]), anchor="lm")
    return int(x + w + pad)


def chip_right(img: Image.Image, right: int, y: int, content: str, fg: str,
               bg: str, size: float = 11, height: int = 24,
               kind: str = "mono") -> int:
    d = ImageDraw.Draw(img)
    w = d.textlength(content, font=font(size, kind)) + 18
    x = right - w
    d.rounded_rectangle([x, y, right, y + height], radius=height / 2,
                        fill=hx(bg))
    d.text((x + 9, y + height / 2), content, font=font(size, kind),
           fill=hx(fg), anchor="lm")
    return int(x)


def chip_left(img: Image.Image, x: int, y: int, content: str, fg: str,
              bg: str, size: float = 11, height: int = 22,
              kind: str = "mono") -> int:
    d = ImageDraw.Draw(img)
    w = d.textlength(content, font=font(size, kind)) + 16
    d.rounded_rectangle([x, y, x + w, y + height], radius=height / 2,
                        fill=hx(bg))
    d.text((x + 8, y + height / 2), content, font=font(size, kind),
           fill=hx(fg), anchor="lm")
    return int(x + w)


def tick(img: Image.Image, x: float, y: float, color: str,
         size: float = 11) -> None:
    d = ImageDraw.Draw(img)
    d.line([(x, y), (x + size * 0.38, y + size * 0.42)], fill=hx(color),
           width=2)
    d.line([(x + size * 0.38, y + size * 0.42), (x + size, y - size * 0.38)],
           fill=hx(color), width=2)


def rich_line(img: Image.Image, x: float, y: float,
              runs: list[tuple[str, str, str]], size: float) -> float:
    d = ImageDraw.Draw(img)
    cursor = float(x)
    for content, color, kind in runs:
        d.text((cursor, y), content, font=font(size, kind),
               fill=hx(color), anchor="ls")
        cursor += measure(content, size, kind)
    return cursor


# ---------------------------------------------------------------------------
# hero copy — zh / en; the sheet values are the shipped quickstart record
# ---------------------------------------------------------------------------
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 交底记录核查",
        title=("dsh-safety-", "brief-check"),
        value=("核完一份交底记录，拿到", "「哪一条、哪一栏、怎么补」清单。"),
        sub="只列材料内部能逐条指认的差异，合规结论留给审核人。",
        meta=[("safety_brief_check", "mono"), (" · 7 条规则 · ", "cjk"),
              ("SB-001 .. SB-007", "mono")],
        foot="Apache-2.0 · 只读材料 · 不联网 · 不调用模型 · 不写盘",
        sheet_title="安全技术交底记录",
        material_chip="material · JSON | YAML",
        file_chip="SB-001-unsafe.json",
        labels=["工程名称", "交底部位", "交底日期", "施工日期", "交底人",
                "专职安全员", "被交底人", "签字", "工种", "交底内容"],
        empty="未填写",
        fix="补正线索：补填表头字段 · 补齐签字栏",
        handoff="safety_brief_check -> issues[] 2 · skipped[] 5",
        source="samples/quickstart/expected/result.json",
        run_head="本次运行",
        issue_unit="条差异",
        skipped_head="未执行",
        reasons=["栏目未配置", "未提供工种", "名单相符", "日期在先", "三词齐备"],
        findings=[("SB-005", "缺交底人"), ("SB-006", "缺签字位")],
        empty_note="空清单 ≠ 通过",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · briefing-record checker",
        title=("dsh-safety-", "brief-check"),
        value=("One record in, the exact list out:", "rule · column · gap · fix."),
        sub="Only what the record can prove — the verdict stays human.",
        meta=[("safety_brief_check", "mono"), (" · 7 rules · ", "cjk"),
              ("SB-001 .. SB-007", "mono")],
        foot="Apache-2.0 · read-only · no network · no model call · no file written",
        sheet_title="SAFETY BRIEFING RECORD",
        material_chip="material · JSON | YAML",
        file_chip="SB-001-unsafe.json",
        labels=["Project", "Section", "Briefed on", "Work starts", "Briefer",
                "Safety officer", "Recipients", "Signatures", "Trades",
                "Content"],
        empty="not filled",
        fix="what to fix: fill the header field · add the signature slot",
        handoff="safety_brief_check -> issues[] 2 · skipped[] 5",
        source="samples/quickstart/expected/result.json",
        run_head="THIS RUN",
        issue_unit="issues",
        skipped_head="SKIPPED",
        reasons=["requiredFields unset", "workTrades unset", "names matched",
                 "dates ordered", "terms present"],
        findings=[("SB-005", "missing briefer"), ("SB-006", "no signature slot")],
        empty_note="empty list ≠ pass",
    ),
}

# The record drawn on the sheet — samples/quickstart/input/SB-001-unsafe.json.
# `None` is the empty 交底人 cell that parse.ts drops, which is exactly why
# SB-005 and SB-006 fire on this run.
SHEET_VALUES = [
    ("某某厂房工程", "二层结构"),
    ("2026-03-10", "2026-03-12"),
    (None, "孙工"),
    (["李四", "王五", "赵六"], ["李四", "王五", "赵六"]),
    ("钢筋工 · 木工", ["危险", "操作规程", "应急"]),
]


def draw_sheet(img: Image.Image, s: dict, h: dict) -> Image.Image:
    """The briefing record itself, with the two findings pinned to their cell."""
    x0, y0, x1, y1 = 632, 44, 1128, 532
    img = card(img, (x0, y0, x1, y1), s, radius=22, shadow=26)
    d = ImageDraw.Draw(img)
    inner = x0 + 24
    right = x1 - 24

    # title bar
    chip_left(img, inner, 58, h["material_chip"], s["accent"], s["pill"],
              size=11, height=24)
    chip_right(img, right, 58, h["file_chip"], s["faint"], s["band"],
               size=11, height=24)
    put(img, (inner, 106), h["sheet_title"], 20, "cjk_bold", s["text"],
        max_w=right - inner, what="sheet title")
    put(img, (inner, 128), f"samples/quickstart/input/{h['file_chip']}", 11,
        "mono", s["faint"], max_w=right - inner, what="sheet path")
    d.line([inner, 142, right, 142], fill=hx(s["grid"]), width=1)

    # form grid: two columns, five rows
    col1, col2 = inner, 892
    col1_w, col2_w = 212, right - col2
    rows = [172, 226, 280, 334, 388]
    d.line([col2 - 20, 152, col2 - 20, 430], fill=hx(s["grid"]), width=1)
    for row_y in rows[1:]:
        d.line([inner, row_y - 16, right, row_y - 16], fill=hx(s["grid"]),
               width=1)
    for column_x, column_w, key in ((col1, col1_w, 0), (col2, col2_w, 1)):
        for index, row_y in enumerate(rows):
            put(img, (column_x, row_y), h["labels"][index * 2 + key], 11.5,
                "cjk", s["faint"], max_w=column_w - 8, what="field label")

    # row 1 — project / section
    put(img, (col1, 196), SHEET_VALUES[0][0], 16.5, "cjk_bold", s["text"],
        max_w=col1_w - 8, what="project")
    put(img, (col2, 196), SHEET_VALUES[0][1], 16.5, "cjk_bold", s["text"],
        max_w=col2_w - 8, what="section")
    # row 2 — briefed / work start
    put(img, (col1, 250), SHEET_VALUES[1][0], 16.5, "mono_bold", s["text"],
        max_w=col1_w - 8, what="briefedAt")
    put(img, (col2, 250), SHEET_VALUES[1][1], 16.5, "mono_bold", s["text"],
        max_w=col2_w - 8, what="workStartAt")
    # row 3 — briefer (empty: the two findings) / safety officer
    d.rounded_rectangle([col1 - 4, 292, col1 + col1_w, 316], radius=9,
                        fill=hx(s["band"]), outline=hx(s["warn"]), width=2)
    d.text((col1 + 6, 306), h["empty"], font=font(12.5, "cjk_bold"),
           fill=hx(s["warn"]), anchor="ls")
    tag_right = col1 + col1_w - 6
    chip_right(img, tag_right, 294, "SB-006", s["danger"], s["pill"], size=11,
               height=20)
    chip_right(img, tag_right - 58, 294, "SB-005", s["danger"], s["pill"],
               size=11, height=20)
    put(img, (col2, 304), SHEET_VALUES[2][1], 16.5, "cjk_bold", s["text"],
        max_w=col2_w - 8, what="safety officer")
    # row 4 — recipients / signatures (all three matched: SB-002 finds nothing)
    put(img, (col1, 358), " · ".join(SHEET_VALUES[3][0]), 16.5, "cjk_bold",
        s["text"], max_w=col1_w - 8, what="recipients")
    cursor = col2
    for person in SHEET_VALUES[3][1]:
        text_w = measure(person, 12.5, "cjk")
        chip_w = text_w + 37
        chip_left(img, cursor, 346, person, s["ok"], s["band"], size=12.5,
                  height=24, kind="cjk")
        tick(img, cursor + 10 + text_w + 4, 359, s["ok"], size=11)
        cursor += chip_w + 8
    if cursor - 8 > col2 + col2_w + 0.5:
        raise SystemExit("FATAL: signature chips overflow the form grid")
    # row 5 — trades / content terms
    put(img, (col1, 412), SHEET_VALUES[4][0], 16.5, "cjk_bold", s["text"],
        max_w=col1_w - 8, what="trades")
    cursor = col2
    for term in SHEET_VALUES[4][1]:
        text_w = measure(term, 11.5, "cjk")
        chip_w = text_w + 33
        chip_left(img, cursor, 400, term, s["ok"], s["band"], size=11.5,
                  height=22, kind="cjk")
        tick(img, cursor + 8 + text_w + 4, 412, s["ok"], size=9)
        cursor += chip_w + 8
    if cursor - 8 > col2 + col2_w + 0.5:
        raise SystemExit("FATAL: term chips overflow the form grid")

    # footer: what to fix, then the handoff to the report
    d = ImageDraw.Draw(img)
    d.line([inner, 440, right, 440], fill=hx(s["grid"]), width=1)
    d.ellipse([inner, 451, inner + 7, 458], fill=hx(s["warn"]))
    put(img, (inner + 16, 460), h["fix"], 12, "cjk", s["sub"],
        max_w=right - inner - 16, what="fix line")
    put(img, (inner, 486), h["handoff"], 11.5, "mono_bold", s["accent"],
        max_w=right - inner, what="handoff")
    put(img, (inner, 508), h["source"], 11, "mono", s["faint"],
        max_w=right - inner, what="source path")
    return img


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    h = HERO[lang]
    W, H = 1440, 576
    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = glow(img, 1180, 60, 380, s["accent"], s["glow"])
    img = glow(img, 160, 556, 300, s["accent"], max(8, s["glow"] // 3))

    m, col_w = 56, 548
    d = ImageDraw.Draw(img)

    # ---- left copy column ---------------------------------------------------
    pill(img, (m, 44), h["kicker"], s, size=16)
    d = ImageDraw.Draw(img)

    title_size = fit_lines(list(h["title"]), "mono_bold", col_w, 58, 50)
    for line in h["title"]:
        require_w(line, title_size, "mono_bold", col_w, "hero title")
    d.text((m - 1, 138), h["title"][0], font=font(title_size, "mono_bold"),
           fill=hx(s["text"]), anchor="ls")
    d.text((m - 1, 200), h["title"][1], font=font(title_size, "mono_bold"),
           fill=hx(s["accent"]), anchor="ls")

    value_size = fit_lines(list(h["value"]), "cjk_bold", col_w,
                           34 if lang == "zh" else 33, 28)
    for index, line in enumerate(h["value"]):
        require_w(line, value_size, "cjk_bold", col_w, "hero value line")
        d.text((m, 268 + index * 44), line, font=font(value_size, "cjk_bold"),
               fill=hx(s["text"]), anchor="ls")

    sub_size = fit(h["sub"], "cjk", col_w, 21, 16)
    require_w(h["sub"], sub_size, "cjk", col_w, "hero subtitle")
    d.text((m, 364), h["sub"], font=font(sub_size, "cjk"), fill=hx(s["sub"]),
           anchor="ls")

    meta_end = m
    for label, kind in h["meta"]:
        meta_end += measure(label, 14, kind)
    if meta_end > m + col_w:
        raise SystemExit("FATAL: hero meta overflows")
    rich_line(img, m + 1, 410,
              [(label, s["faint"], kind) for label, kind in h["meta"]], 14)

    d = ImageDraw.Draw(img)
    d.line([m + 1, 446, m + col_w - 4, 446], fill=hx(s["grid"]), width=2)
    require_w(h["foot"], 14, "cjk", col_w, "hero footer")
    d.text((m + 1, 470), h["foot"], font=font(14, "cjk"), fill=hx(s["faint"]),
           anchor="ls")

    # ---- right: the record sheet -------------------------------------------
    img = draw_sheet(img, s, h)
    d = ImageDraw.Draw(img)

    # ---- right rail: the run -------------------------------------------------
    img = card(img, (1144, 44, 1384, 300), s, radius=20, shadow=22)
    d = ImageDraw.Draw(img)
    put(img, (1162, 72), h["run_head"], 11.5, "cjk_bold", s["faint"],
        max_w=204, what="run head")
    put(img, (1162, 128), "2", 40, "mono_bold", s["accent"], max_w=60,
        what="issue count")
    put(img, (1200, 126), h["issue_unit"], 12.5, "cjk", s["sub"], max_w=150,
        what="issue unit")
    for index, (label, count, color) in enumerate(
            (("error", 0, s["danger"]), ("warn", 2, s["warn"]),
             ("info", 0, s["accent"]))):
        y = 158 + index * 24
        d.ellipse([1166, y - 9, 1175, y], fill=hx(color))
        put(img, (1186, y), label, 12, "mono", s["sub"], max_w=80,
            what="severity label")
        put(img, (1366, y), str(count), 12.5, "mono_bold", color, anchor="rs",
            max_w=60, what="severity count")
    d.line([1162, 232, 1366, 232], fill=hx(s["grid"]), width=1)
    for index, (rule, label) in enumerate(h["findings"]):
        y = 256 + index * 26
        put(img, (1162, y), rule, 12.5, "mono_bold", s["text"], max_w=52,
            what="finding rule")
        put(img, (1222, y), label, 12, "cjk", s["sub"], max_w=142,
            what="finding text")

    # ---- right rail: skipped ledger ------------------------------------------
    img = card(img, (1144, 312, 1384, 532), s, radius=20, shadow=22)
    d = ImageDraw.Draw(img)
    put(img, (1162, 342), h["skipped_head"], 11.5, "cjk_bold", s["faint"],
        max_w=160, what="skipped head")
    put(img, (1366, 344), "5", 20, "mono_bold", s["sub"], anchor="rs",
        max_w=40, what="skipped count")
    order = ["SB-001", "SB-004", "SB-002", "SB-003", "SB-007"]
    for index, reason in enumerate(h["reasons"]):
        y = 378 + index * 27
        put(img, (1162, y), order[index], 12, "mono_bold", s["faint"],
            max_w=48, what="skipped rule")
        put(img, (1214, y), reason, 12, "cjk", s["sub"], max_w=152,
            what="skipped reason")
    put(img, (1162, 512), h["empty_note"], 11.5, "cjk_bold", s["warn"],
        max_w=204, what="empty note")

    name = f"{NAME}-hero-{lang}-{skin}.webp"
    img.save(os.path.join(OUT, name), "WEBP", quality=92, method=6)
    print(f"wrote {name} ({W}x{H})")


# ---------------------------------------------------------------------------
# flow SVG: record -> seven gates -> issues[] / skipped[] -> report -> reviewer
# ---------------------------------------------------------------------------
GATES = [
    # (rule, what it reads, severity, exit)
    ("SB-001", "fields{} >= required", "info", "skipped[]"),
    ("SB-002", "recipients vs signers", "error", "issues[]"),
    ("SB-003", "briefedAt <= workStart", "warn", "skipped[]"),
    ("SB-004", "trades >= workTrades", "warn", "skipped[]"),
    ("SB-005", "project, briefer", "warn", "issues[]"),
    ("SB-006", "fields{} · 3 parties", "warn", "issues[]"),
    ("SB-007", "fields{} · terms[3]", "warn", "skipped[]"),
]

# The quickstart run, resolved by src/check.ts: SB-002/003/007 ran and found no
# difference; SB-001/004 never ran (requiredFields / workTrades unset). Both
# kinds land in skipped[] — that is the point of the second ledger.
SKIPPED_ROWS = [
    ("SB-001", "requiredFields unset", "not run"),
    ("SB-004", "workTrades unset", "not run"),
    ("SB-002", "matched · no difference", "no diff"),
    ("SB-003", "ordered · no difference", "no diff"),
    ("SB-007", "all 3 terms · no difference", "no diff"),
]
ISSUE_ROWS = [
    ("SB-005", "warn", "locator {}"),
    ("SB-006", "warn", "locator {}"),
]


class Svg:
    def __init__(self, s: dict, w: int, h: int, title: str, desc: str) -> None:
        self.s = s
        self.w, self.h = w, h
        self.parts: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(desc)}</desc>',
            "<defs>",
            f'<linearGradient id="bg" x1="0" y1="0" x2="0.2" y2="1">'
            f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
            f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>',
            f'<filter id="soft" x="-30%" y="-30%" width="160%" height="180%">'
            f'<feDropShadow dx="0" dy="7" stdDeviation="9" '
            f'flood-color="{s["shadow"]}" flood-opacity="{s["shadow_op"]}"/>'
            f'</filter>',
            f'<pattern id="dots" width="24" height="24" '
            f'patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" r="1.2" '
            f'fill="{s["dot"]}"/></pattern>',
            "</defs>",
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="url(#bg)"/>',
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="url(#dots)" '
            f'opacity="{s["dot_op"]}"/>',
        ]

    # -- primitives ---------------------------------------------------------
    def rect(self, x: float, y: float, w: float, h: float, *, fill: str,
             rx: float = 0, stroke: str | None = None, sw: float = 1.5,
             shadow: bool = False, opacity: float | None = None) -> None:
        attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'width="{w:.1f}"',
                 f'height="{h:.1f}"', f'rx="{rx:.1f}"', f'fill="{fill}"']
        if stroke:
            attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if shadow:
            attrs.append('filter="url(#soft)"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.parts.append(f'<rect {" ".join(attrs)}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, *, stroke: str,
             sw: float = 1.2, opacity: float | None = None) -> None:
        attrs = [f'x1="{x1:.1f}"', f'y1="{y1:.1f}"', f'x2="{x2:.1f}"',
                 f'y2="{y2:.1f}"', f'stroke="{stroke}"', f'stroke-width="{sw}"',
                 'stroke-linecap="round"']
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.parts.append(f'<line {" ".join(attrs)}/>')

    def path(self, d: str, *, stroke: str, sw: float = 1.5) -> None:
        self.parts.append(f'<path d="{d}" fill="none" stroke="{stroke}" '
                          f'stroke-width="{sw}" stroke-linecap="round" '
                          f'stroke-linejoin="round"/>')

    def circle(self, cx: float, cy: float, r: float, *, fill: str,
               stroke: str | None = None, sw: float = 1.4) -> None:
        attrs = [f'cx="{cx:.1f}"', f'cy="{cy:.1f}"', f'r="{r:.1f}"',
                 f'fill="{fill}"']
        if stroke:
            attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
        self.parts.append(f'<circle {" ".join(attrs)}/>')

    def text(self, x: float, y: float, content: str, size: float, fill: str,
             *, kind: str = "cjk", weight: int | None = None,
             anchor: str = "start", max_w: float | None = None,
             min_x: float | None = None, what: str = "text") -> float:
        if size < 11:
            raise SystemExit(f"FATAL: {what} is {size}px, below the 11px "
                             f"annotation floor: {content!r}")
        got = measure(content, size, kind)
        if max_w is not None and anchor == "start" and got > max_w + 0.4:
            raise SystemExit(f"FATAL: {what} overflows: {content!r} needs "
                             f"{got:.1f}px > {max_w:.0f}px")
        if min_x is not None and anchor == "end" and x - got < min_x - 0.4:
            raise SystemExit(f"FATAL: {what} overflows left: {content!r} needs "
                             f"{got:.1f}px before {x:.0f} (limit {min_x:.0f})")
        family = FONT_CSS_MONO if kind.startswith("mono") else FONT_CSS_SANS
        attrs = [f'x="{x:.1f}"', f'y="{y:.3f}"', f'fill="{fill}"',
                 f'font-family="{family}"', f'font-size="{size}"']
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        self.parts.append(f'<text {" ".join(attrs)}>{escape(content)}</text>')
        return got

    def chip_left(self, x: float, y: float, label: str, *, fg: str, bg: str,
                  size: float = 11, height: float = 22,
                  kind: str = "mono") -> float:
        pad = 8
        w = measure(label, size, kind) + pad * 2
        self.rect(x, y, w, height, fill=bg, rx=height / 2)
        self.text(x + pad, y + height / 2 + size * 0.36, label, size, fg,
                  kind=kind)
        return x + w

    def chip_right(self, right: float, y: float, label: str, *, fg: str,
                   bg: str, size: float = 11, height: float = 22,
                   kind: str = "mono") -> float:
        pad = 8
        w = measure(label, size, kind) + pad * 2
        self.rect(right - w, y, w, height, fill=bg, rx=height / 2)
        self.text(right - pad, y + height / 2 + size * 0.36, label, size, fg,
                  kind=kind, anchor="end")
        return right - w

    def arrow_right(self, x1: float, x2: float, y: float, color: str,
                    sw: float = 1.6) -> None:
        self.path(f"M{x1:.1f} {y:.1f}H{x2 - 5:.1f}", stroke=color, sw=sw)
        self.path(f"M{x2 - 6:.1f} {y - 4:.1f}L{x2 - 0.5:.1f} {y:.1f}"
                  f"L{x2 - 6:.1f} {y + 4:.1f}", stroke=color, sw=sw)

    def arrow_down(self, x: float, y1: float, y2: float, color: str,
                   sw: float = 1.4) -> None:
        self.path(f"M{x:.1f} {y1:.1f}V{y2 - 5:.1f}", stroke=color, sw=sw)
        self.path(f"M{x - 4:.1f} {y2 - 6:.1f}L{x:.1f} {y2 - 0.5:.1f}"
                  f"L{x + 4:.1f} {y2 - 6:.1f}", stroke=color, sw=sw)

    def render(self) -> str:
        self.parts.append("</svg>")
        return "\n".join(self.parts) + "\n"


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    v = Svg(
        s, 1100, 660,
        "dsh-safety-brief-check — one briefing record, seven gates, two ledgers",
        "Left: the record parsed into BriefInput — project, briefer (empty in the "
        "sample), briefedAt, workStartAt, recipients[], signers[], trades[] and "
        "fields{}. Middle: the seven gates of rules/safety-brief-check.yaml in "
        "pack order, each reading named fields and exiting into exactly one of "
        "issues[] or skipped[]. Right: the report for the sample run — issues[] "
        "holds SB-005 and SB-006 at warn; skipped[] holds five entries (SB-001 "
        "and SB-004 never ran because requiredFields and workTrades are unset; "
        "SB-002, SB-003 and SB-007 ran and found no difference). makeReport() "
        "merges both arrays; the reviewer decides; skipped is not a pass. Footer: "
        "severity caps by evidence kind and the read-only, offline bounds.",
    )
    text, sub, faint = s["text"], s["sub"], s["faint"]
    accent, warn, danger = s["accent"], s["warn"], s["danger"]

    # ---- header --------------------------------------------------------------
    v.text(36, 58, NAME, 27, text, kind="cjk_bold", weight=700, max_w=620,
           what="title")
    v.text(36, 84, "one briefing record · seven gates · two ledgers", 12.5, sub,
           max_w=620, what="subtitle")
    v.chip_right(1064, 32, "rules/safety-brief-check.yaml · v2026.2",
                 fg=accent, bg=s["pill"], size=11, height=26)
    v.text(36, 108, "IN   ·  file | material · JSON / YAML · one flat record",
           11, faint, kind="mono", max_w=520, what="IN line")
    v.text(1064, 108, "OUT  ·  summary · issues[] · skipped[] · markdown",
           11, faint, kind="mono", anchor="end", min_x=520, what="OUT line")
    v.line(36, 122, 1064, 122, stroke=s["rule"], sw=1, opacity=0.75)

    # ---- left panel: record -> BriefInput ------------------------------------
    v.rect(36, 136, 250, 424, fill=s["panel"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(52, 165, "material", 15, text, kind="cjk_bold", weight=700,
           max_w=110, what="material head")
    v.chip_right(270, 150, "YAML", fg=faint, bg=s["band"], size=11, height=20)
    v.chip_right(218, 150, "JSON", fg=faint, bg=s["band"], size=11, height=20)
    rows = [
        ("project", "set", accent),
        ("briefer", "(empty)", warn),
        ("briefedAt", "2026-03-10", sub),
        ("workStartAt", "2026-03-12", sub),
        ("recipients[]", "3", text),
        ("signers[]", "3", text),
        ("trades[]", "2", text),
        ("fields{}", "9", text),
    ]
    for index, (token, value, color) in enumerate(rows):
        y = 196 + index * 23
        if token == "briefer":
            v.rect(46, y - 15, 224, 22, fill=s["band"], rx=7)
        v.text(52, y, token, 13, text, kind="mono", max_w=110,
               what="field token")
        v.text(270, y, value, 13, color, kind="mono", anchor="end", min_x=180,
               what="field value")
    v.line(52, 372, 270, 372, stroke=s["rule"], sw=1)
    v.arrow_down(161, 376, 392, accent)
    v.text(52, 414, "parse.ts", 15, text, kind="cjk_bold", weight=700,
           max_w=110, what="parse head")
    v.chip_left(52, 426, "COLUMNS alias", fg=accent, bg=s["pill"], size=11,
                height=20)
    v.chip_left(158, 426, "splitNames()", fg=accent, bg=s["pill"], size=11,
                height=20)
    v.chip_left(52, 452, "trim()", fg=accent, bg=s["pill"], size=11, height=20)
    v.chip_left(110, 452, "nameKey()", fg=accent, bg=s["pill"], size=11,
                height=20)
    v.text(52, 496, "BriefInput", 12.5, accent, kind="cjk_bold", weight=700,
           max_w=180, what="briefinput head")
    v.text(52, 516, "8 fields · 4 lists", 11, sub, kind="mono", max_w=180,
           what="briefinput note")
    v.text(52, 540, "read-only · original untouched", 11, faint, kind="mono",
           max_w=210, what="read-only note")

    # ---- middle panel: the seven gates ---------------------------------------
    v.rect(306, 136, 372, 424, fill=s["panel"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(322, 165, "check.ts", 15, text, kind="cjk_bold", weight=700,
           max_w=120, what="gates head")
    v.text(662, 165, "7 gates · pack order", 11, faint, kind="mono",
           anchor="end", min_x=470, what="gates note")
    v.line(322, 176, 662, 176, stroke=s["rule"], sw=1)
    for index, (rule, reads, sev, exit_to) in enumerate(GATES):
        cy = 200 + index * 40
        issue = exit_to == "issues[]"
        v.rect(322, cy - 16, 340, 32, fill=(s["cell"] if issue else s["band"]),
               rx=9)
        v.rect(322, cy - 16, 3, 32, fill=(danger if issue else s["edge"]), rx=1.5)
        v.text(332, cy + 4.5, rule, 13, text, kind="mono_bold", weight=700,
               max_w=52, what="gate rule")
        v.text(392, cy + 4.5, reads, 13, sub, kind="mono", max_w=156,
               what="gate reads")
        v.text(558, cy + 4, sev, 11, (danger if sev == "error" else (
            warn if sev == "warn" else accent)), kind="mono", max_w=34,
            what="gate severity")
        v.chip_right(662, cy - 11, exit_to, fg=(danger if issue else faint),
                     bg=s["pill"], size=11, height=22)
    v.line(322, 486, 662, 486, stroke=s["rule"], sw=1)
    v.text(322, 508, "config → rulesFile · disabledRules · onlyRules", 11,
           sub, kind="mono", max_w=340, what="config line 1")
    v.text(322, 526, "skipNotes · timeoutMs → skipped[]", 11, faint,
           kind="mono", max_w=340, what="config line 2")
    v.text(322, 544, "every rule that cannot run names itself in skipped[]",
           11, faint, kind="mono", max_w=340, what="gates note 2")

    # ---- right panel: report, two ledgers, reviewer --------------------------
    v.rect(698, 136, 366, 448, fill=s["panel"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(714, 165, "report", 15, text, kind="cjk_bold", weight=700,
           max_w=110, what="report head")
    v.chip_right(1048, 150, "makeReport() · v2026.2", fg=accent, bg=s["pill"],
                 size=11, height=22)
    v.text(714, 190, "error 0 · warn 2 · info 0", 11, sub, kind="mono",
           max_w=220, what="summary")
    v.text(1048, 190, "skippedCount 5", 11, faint, kind="mono", anchor="end",
           min_x=880, what="skipped count")

    # issues[] band
    v.text(714, 220, "issues[]", 15, text, kind="cjk_bold", weight=700,
           max_w=90, what="issues label")
    v.text(790, 220, "2", 15, danger, kind="mono_bold", weight=700, max_w=20,
           what="issues count")
    for index, (rule, sev, locator) in enumerate(ISSUE_ROWS):
        top = 232 + index * 46
        v.rect(714, top, 334, 40, fill=s["cell"], rx=10, stroke=s["edge"],
               sw=1)
        v.text(728, top + 16, rule, 13, text, kind="mono_bold", weight=700,
               max_w=56, what="issue rule")
        v.text(786, top + 16, sev, 11, warn, kind="mono", max_w=34,
               what="issue severity")
        v.text(1034, top + 16, locator, 11, faint, kind="mono",
               anchor="end", min_x=900, what="issue locator")
        v.text(728, top + 33, "found · expected · fix · basis", 11, sub,
               kind="mono", max_w=300, what="issue shape")

    # skipped[] band
    v.text(714, 340, "skipped[]", 15, text, kind="cjk_bold", weight=700,
           max_w=100, what="skipped label")
    v.text(800, 340, "5", 15, faint, kind="mono_bold", weight=700, max_w=20,
           what="skipped count")
    v.text(1048, 340, "reason", 11, faint, kind="mono", anchor="end",
           min_x=950, what="reason label")
    for index, (rule, reason, kind) in enumerate(SKIPPED_ROWS):
        y = 366 + index * 28
        v.circle(722, y - 4, 3.1,
                 fill=(s["edge"] if kind == "not run" else faint))
        v.text(732, y, rule, 13, sub, kind="mono_bold", weight=700, max_w=56,
               what="skipped rule")
        v.text(796, y, reason, 11.5, sub, kind="mono", max_w=250,
               what="skipped reason")
        v.text(1034, y, kind, 11, faint, kind="mono", anchor="end", min_x=960,
               what="skipped kind")
    v.text(714, 508, "skipped[] = not-run + no-difference", 11, warn,
           kind="mono", max_w=320, what="skipped annotation")

    # reviewer
    v.rect(714, 522, 334, 48, fill=s["pill"], rx=12)
    v.text(730, 551, "reviewer", 13, accent, kind="cjk_bold", weight=700,
           max_w=80, what="reviewer")
    v.text(812, 550, "verdict stays human", 11.5, sub, max_w=160,
           what="reviewer note")
    v.text(1036, 550, "wording.ts", 11, faint, kind="mono", anchor="end",
           min_x=940, what="wording guard")

    # ---- connectors ----------------------------------------------------------
    v.arrow_right(286, 306, 320, accent)
    v.arrow_right(678, 698, 320, accent)

    # ---- footer --------------------------------------------------------------
    v.text(36, 614,
           "severity caps → direct: error · derived: <= warn · "
           "institutional: <= info", 11, sub, kind="mono", max_w=760,
           what="caps")
    v.text(1064, 614, "skipped[] != passed", 11, warn, kind="mono",
           anchor="end", min_x=820, what="not a pass")
    v.text(36, 638, "out → markdown · reportJson · DISCLAIMER", 11, faint,
           kind="mono", max_w=420, what="out line")
    v.text(1064, 638, "no network · no model call · no file written", 11,
           faint, kind="mono", anchor="end", min_x=700, what="bounds")
    return v.render()


def main() -> None:
    for skin in ("light", "dark"):
        svg = flow_svg(skin)
        path = os.path.join(OUT, f"{NAME}-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(svg)
        # parse what we just wrote: a malformed SVG must fail here, not on GitHub
        ET.fromstring(svg)
        print(f"wrote {os.path.basename(path)} (1100x660)")

    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            hero(lang, skin)


if __name__ == "__main__":
    main()
