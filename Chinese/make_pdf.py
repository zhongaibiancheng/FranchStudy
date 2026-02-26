# make_dictation_pdf.py
# 生成“全挖空默写练习PDF”和“答案PDF”
# 用法示例：
#   python make_dictation_pdf.py --input poems_27.json --practice_out practice.pdf --answer_out answer.pdf

import argparse
import json
import re
from typing import List, Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont


# -----------------------------
# 1) 中文字体：用内置 CID 字体（无需安装字体文件）
# -----------------------------
def register_cjk_font():
    # STSong-Light 基本覆盖简体中文
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    return "STSong-Light"


# -----------------------------
# 2) 分句：按标点断句（保留标点）
# -----------------------------
SENT_SPLIT_RE = re.compile(r"([^，。！？；：,.!?;:]+[，。！？；：,.!?;:]*)")

def split_to_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []

    # 先把多余空白规整一下
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\r\n", "\n", text)

    # 按段落拆，再按标点拆
    out: List[str] = []
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            continue
        parts = [p.strip() for p in SENT_SPLIT_RE.findall(para) if p.strip()]
        if parts:
            out.extend(parts)
        else:
            out.append(para)
    return out


# -----------------------------
# 3) 全挖空：每个“字” -> "_ _"
#    - 标点/空白保留
# -----------------------------
# 常见中文/英文标点集合（保留）
PUNCT = set("，。！？；：、,.!?;:（）()【】[]《》“”\"'‘’—-…· ")

def blank_all_chars(sentence: str, token: str = "_ _") -> str:
    buf = []
    for ch in sentence:
        if ch in PUNCT or ch.isspace():
            buf.append(ch)
        else:
            # 每个字用“两个下划线中间留空”
            buf.append(token)
    return "".join(buf)


# -----------------------------
# 4) PDF 生成
# -----------------------------
def make_pdf(items: List[Dict[str, Any]], out_path: str, mode: str, blank_token: str):
    font_name = register_cjk_font()

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="默写练习" if mode == "practice" else "答案",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CJKTitle",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F2B5B"),
        spaceAfter=6,
    )

    meta_style = ParagraphStyle(
        "CJKMeta",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "CJKBody",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=12,
        leading=18,
        textColor=colors.black,  # ✅ 绝对不要 None，避免你之前那个 Unknown color None
        spaceAfter=6,
    )

    hint_style = ParagraphStyle(
        "CJKHint",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=10,
    )

    story = []

    for idx, it in enumerate(items, start=1):
        title = (it.get("title") or "").strip()
        author = (it.get("author") or "").strip()
        content = (it.get("content") or "").strip()

        # 标题区
        story.append(Paragraph(f"{idx}. {title}", title_style))
        if author:
            story.append(Paragraph(f"作者：{author}", meta_style))

        if mode == "practice":
            story.append(Paragraph("（请在空白处默写原文）", hint_style))

        # 正文分句
        sents = split_to_sentences(content)

        # 把每句作为单独行打印，保持清晰“默写本”感
        lines = []
        for s in sents:
            if mode == "practice":
                lines.append(blank_all_chars(s, token=blank_token))
            else:
                lines.append(s)

        # 用 <br/> 保证每句换行
        body_html = "<br/>".join([escape_html(x) for x in lines]) if lines else "（无内容）"
        story.append(Paragraph(body_html, body_style))

        # 每篇之间留空
        story.append(Spacer(1, 6 * mm))

        # 分页（最后一篇不加）
        if idx != len(items):
            story.append(PageBreak())

    doc.build(story)


def escape_html(s: str) -> str:
    # Paragraph 使用简易 HTML，需要转义
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )


def load_items(input_path: str) -> List[Dict[str, Any]]:
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 兼容两种：直接数组 or {"items":[...]}
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]

    raise ValueError("JSON结构不正确：需要是数组，或 {\"items\":[...]} 格式")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="poems_27.json")
    ap.add_argument("--practice_out", required=True, help="练习版PDF输出路径")
    ap.add_argument("--answer_out", required=True, help="答案版PDF输出路径")
    ap.add_argument("--blank_token", default="_ _", help="每个字的挖空符号（默认：_ _）")
    args = ap.parse_args()

    items = load_items(args.input)

    make_pdf(items, args.practice_out, mode="practice", blank_token=args.blank_token)
    make_pdf(items, args.answer_out, mode="answer", blank_token=args.blank_token)

    print(f"[OK] practice -> {args.practice_out}")
    print(f"[OK] answer   -> {args.answer_out}")


if __name__ == "__main__":
    main()

