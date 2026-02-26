import argparse
import json
import random
import re
from typing import List, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont


def register_cn_font():
    """
    使用 ReportLab 自带 CID 中文字体（通常无需额外安装字体文件）。
    """
    try:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        return "STSong-Light"
    except Exception:
        return "Helvetica"


def split_to_sentences(text: str) -> List[str]:
    """
    将正文切分为“句子/行”。
    规则：
      1) 先按换行拆
      2) 再按中文标点（。！？；）断句，保留标点在句末
    """
    text = (text or "").strip()
    if not text:
        return []

    parts: List[str] = []
    for block in text.split("\n"):
        block = block.strip()
        if not block:
            continue
        segs = re.split(r"(?<=[。！？；])", block)
        for s in segs:
            s = s.strip()
            if s:
                parts.append(s)
    return parts


def blank_line(line: str, min_len=22, max_len=60) -> str:
    """
    用“横线”替换整句。
    这里用全角下划线，看起来更像中文练习纸的横线。
    """
    # 根据原句长度粗略决定横线长度
    n = max(min_len, min(max_len, int(len(line) * 1.8)))
    return "＿" * n  # 全角下划线


def build_practice_lines(sentences: List[str], keep_ratio: float, rng: random.Random) -> List[Dict]:
    """
    返回结构化行：[{type: 'keep'|'blank', text: ...}]
    保留约 keep_ratio 的句子，其余置空为横线。
    """
    if not sentences:
        return []

    total = len(sentences)
    keep_count = max(1, int(round(total * keep_ratio)))
    keep_count = min(keep_count, total)

    idxs = list(range(total))
    rng.shuffle(idxs)
    keep_set = set(idxs[:keep_count])

    out = []
    for i, s in enumerate(sentences):
        if i in keep_set:
            out.append({"type": "keep", "text": s})
        else:
            out.append({"type": "blank", "text": blank_line(s)})
    return out


def make_pdf(items: List[Dict], out_path: str, mode: str, keep_ratio: float, seed: int):
    font_name = register_cn_font()

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="古诗文默写练习",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CNTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=18,
        leading=22,
        spaceAfter=10,
    )

    meta_style = ParagraphStyle(
        "CNMeta",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=11,
        leading=16,
        spaceAfter=8,
    )

    h_style = ParagraphStyle(
        "CNHeader",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=13,
        leading=18,
        spaceBefore=10,
        spaceAfter=6,
    )

    line_style = ParagraphStyle(
        "CNLine",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=12,
        leading=18,
        spaceAfter=3,
        wordWrap="CJK",
    )

    hint_style = ParagraphStyle(
        "CNHint",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9.5,
        leading=14,
        spaceAfter=10,
    )

    story = []

    # 封面
    if mode == "practice":
        story.append(Paragraph("古诗文默写练习（A4）", title_style))
        story.append(Paragraph("说明：每篇保留约 10% 句子，其余用横线留空，请在横线上默写。", meta_style))
    else:
        story.append(Paragraph("古诗文答案（A4）", title_style))
        story.append(Paragraph("说明：本页为全文答案，用于核对。", meta_style))

    story.append(Spacer(1, 6))

    rng = random.Random(seed)

    for idx, item in enumerate(items, start=1):
        title = item.get("title", "")
        subtitle = item.get("subtitle")
        author = item.get("author", "")
        dynasty = item.get("dynasty", "")
        category = item.get("category", "")
        content = item.get("content", "")

        # 标题
        head = f"{idx}. {title}"
        if subtitle:
            head += f"（{subtitle}）"
        story.append(Paragraph(head, h_style))

        # 元信息
        meta = f"{author} ｜ {dynasty} ｜ {category}"
        story.append(Paragraph(meta, hint_style))

        sentences = split_to_sentences(content)

        if mode == "practice":
            lines = build_practice_lines(sentences, keep_ratio, rng)
            for i, ln in enumerate(lines, start=1):
                story.append(Paragraph(f"{i}. {ln['text']}", line_style))
        else:
            for i, s in enumerate(sentences, start=1):
                story.append(Paragraph(f"{i}. {s}", line_style))

        story.append(Spacer(1, 10))

        # 分页策略：每 6 篇分页一次
        if idx % 6 == 0 and idx != len(items):
            story.append(PageBreak())

    doc.build(story)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="poems_27.json 路径")
    ap.add_argument("--out", required=True, help="输出 PDF 路径")
    ap.add_argument("--mode", choices=["practice", "answer"], default="practice", help="practice=练习版 / answer=答案版")
    ap.add_argument("--keep_ratio", type=float, default=0.10, help="每篇保留句子比例（默认 0.10）")
    ap.add_argument("--seed", type=int, default=2026, help="随机种子，保证每次留空位置一致")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    if not isinstance(items, list) or not items:
        raise ValueError("JSON 里未找到 items 数组或为空")

    make_pdf(items, args.out, args.mode, args.keep_ratio, args.seed)
    print(f"[OK] 输出：{args.out}")


if __name__ == "__main__":
    main()

