# make_tianzige_pdf.py
# 生成田字格默写练习PDF + 答案PDF
# 用法：
#   python make_tianzige_pdf.py --input poems_27.json --practice_out practice.pdf --answer_out answer.pdf
#
# JSON 结构支持：
# 1) [{"title": "...", "author": "...", "content": "..."} ...]
# 2) {"items":[{"title": "...", "author": "...", "content": "..."} ...]}

import argparse
import json
import re
from typing import List, Dict, Any, Tuple

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Table, TableStyle

# -----------------------------
# 中文字体（无需本地字体文件）
# -----------------------------
def register_cjk_font():
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    return "STSong-Light"


# -----------------------------
# 分句（保留标点）
# -----------------------------
SENT_SPLIT_RE = re.compile(r"([^，。！？；：、,.!?;:\n]+[，。！？；：、,.!?;:]*)")

def split_to_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    # 段落按换行切开，再按标点切句
    out = []
    for para in re.split(r"\r?\n+", text):
        para = para.strip()
        if not para:
            continue
        parts = [p.strip() for p in SENT_SPLIT_RE.findall(para) if p.strip()]
        out.extend(parts if parts else [para])
    return out


# -----------------------------
# 田字格绘制
# -----------------------------
PUNCT = set("，。！？；：、,.!?;:（）()【】[]《》“”\"'‘’—-…· ")

from reportlab.lib import colors
from reportlab.pdfgen import canvas

from reportlab.lib import colors
from reportlab.pdfgen import canvas

def draw_tianzige(
    c: canvas.Canvas,
    x: float,
    y: float,
    size: float,
    border_color=colors.HexColor("#000000"),  # 外框颜色（蓝一点）
    cross_color=colors.HexColor("#000000"),   # 十字虚线颜色（浅一点）
):
    """
    田字格（无背景）：
    - 外框：实线（border_color）
    - 内部十字：虚线（cross_color），并且不与外框连接（留 gap）
    """
    c.saveState()

    # ---- 外框：实线 ----
    c.setStrokeColor(border_color)
    c.setLineWidth(0.9)
    c.setDash()  # 清除虚线
    c.rect(x, y, size, size, stroke=1, fill=0)

    # ---- 十字：虚线（不连外框）----
    gap = max(1.2, size * 0.08)  # 中线离外框留白
    cx = x + size / 2
    cy = y + size / 2

    c.setStrokeColor(cross_color)
    c.setLineWidth(0.45)
    dash_len = max(1.0, size * 0.10)  # 虚线密度（可调 0.08~0.14）
    c.setDash(dash_len, dash_len)

    # 竖虚线
    c.line(cx, y + gap, cx, y + size - gap)
    # 横虚线
    c.line(x + gap, cy, x + size - gap, cy)

    # 复原
    c.setDash()
    c.restoreState()

def draw_char_center(c: canvas.Canvas, ch: str, x: float, y: float, size: float, font_name: str, font_size: float):
    """把字居中写在田字格中"""
    c.setFont(font_name, font_size)
    # 近似居中：用字符串宽度 + 上移一点点视觉更居中
    w = pdfmetrics.stringWidth(ch, font_name, font_size)
    cx = x + (size - w) / 2
    cy = y + (size - font_size) / 2 - 0.5  # 微调
    c.setFillColor(colors.black)
    c.drawString(cx, cy, ch)

# -----------------------------
# 排版参数（可调）
# -----------------------------
PAGE_W, PAGE_H = A4
MARGIN_X = 16 * mm
MARGIN_TOP = 14 * mm
MARGIN_BOTTOM = 14 * mm

CELL = 10 * mm          # 田字格边长（推荐 9~11mm）
GAP_X = 1.2 * mm        # 格子间距
LINE_GAP = 2.2 * mm     # 行间距（额外距离）
PUNCT_ADV = 4.2 * mm    # 标点占位宽度（不进格子）

TITLE_FONT = 14
META_FONT = 10.5
BODY_FONT = 14          # 写进格子的字大小（可调：12~15）


# -----------------------------
# 页眉/标题
# -----------------------------
def new_page(c: canvas.Canvas, page_title: str, font_name: str):
    c.showPage()
    c.setFont(font_name, 10)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 8 * mm, page_title)


def draw_section_header(c: canvas.Canvas, idx: int, title: str, author: str, mode: str, font_name: str, y: float,dynasty:str) -> float:
    """
    画一个“卡片式”标题块
    - 增加 padding_top 让标题不贴上边
    - box_h 稍微加高，容纳两行中文更舒服
    返回新的 y（往下走）
    """
    x0 = MARGIN_X
    w = PAGE_W - 2 * MARGIN_X

    # ✅ 高度略加大：原来 16mm，建议 20~22mm
    box_h = 22 * mm

    # ✅ 内边距：控制“标题往下”
    pad_x = 10
    pad_top = 6 * mm  # 你想更往下就改 7mm / 8mm
    pad_bottom = 4 * mm

    # 背景
    c.setFillColor(colors.HexColor("#EFF6FF"))
    c.setStrokeColor(colors.HexColor("#BFDBFE"))
    c.roundRect(x0, y - box_h, w, box_h, 10, stroke=1, fill=1)

    # 计算第一行（标题）baseline：从框顶往下 pad_top
    # ReportLab drawString 的 y 是 baseline，所以我们要减去一点“字体上沿补偿”
    title_y = (y - pad_top) - (TITLE_FONT * 0.85)

    # 标题
    c.setFillColor(colors.HexColor("#0F2B5B"))
    c.setFont(font_name, TITLE_FONT)
    c.drawString(x0 + pad_x, title_y, f"{idx}. {title}")

    # 作者/右侧提示：在标题下方一行
    meta_y = title_y - 12  # 这一行间距你也可调 11/13
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont(font_name, META_FONT)
    if author:
        c.drawString(x0 + pad_x, meta_y, f"作者：({dynasty}){author}")

    if mode == "practice":
        c.setFillColor(colors.HexColor("#64748B"))
        c.setFont(font_name, 9.5)
        c.drawRightString(x0 + w - pad_x, meta_y, "田字格默写（不写标点）")

    # ✅ 框下面留一点空白
    return y - box_h - 6 * mm



# -----------------------------
# 核心：正文写田字格
# -----------------------------
def ensure_space(c: canvas.Canvas, font_name: str, page_title: str, y: float, need_h: float) -> float:
    """如果 y 不够了就换页，返回新的 y"""
    if y - need_h < MARGIN_BOTTOM:
        new_page(c, page_title, font_name)
        return PAGE_H - MARGIN_TOP
    return y


def render_text_as_tianzige(
    c: canvas.Canvas,
    text: str,
    mode: str,
    font_name: str,
    page_title: str,
    y: float
) -> float:
    """
    以句为单位渲染：每个字一个田字格，标点直接画
    返回渲染后的 y
    """
    sentences = split_to_sentences(text)
    if not sentences:
        return y

    max_x = PAGE_W - MARGIN_X
    x = MARGIN_X
    # 当前行基线：田字格用左下角 y_box
    # 我们用 y 代表“当前行顶部”，格子画在 y - CELL
    for sent in sentences:
        # 句子开始前确保至少一行空间
        y = ensure_space(c, font_name, page_title, y, need_h=(CELL + LINE_GAP))
        x = MARGIN_X

        for ch in sent:
            if ch.isspace():
                continue

            # 标点：直接画，不进格子
            if ch in PUNCT:
                # 如果标点也要换行
                if x + PUNCT_ADV > max_x:
                    y -= (CELL + LINE_GAP)
                    y = ensure_space(c, font_name, page_title, y, need_h=(CELL + LINE_GAP))
                    x = MARGIN_X

                c.setFillColor(colors.black)
                c.setFont(font_name, BODY_FONT)
                # 标点放在格子中线附近，视觉更舒服
                c.drawString(x + 0.5, y - CELL/2 - BODY_FONT/2 + 2, ch)
                x += PUNCT_ADV
                continue

            # 字：画格子
            if x + CELL > max_x:
                y -= (CELL + LINE_GAP)
                y = ensure_space(c, font_name, page_title, y, need_h=(CELL + LINE_GAP))
                x = MARGIN_X

            y_box = y - CELL
            draw_tianzige(c, x, y_box, CELL)

            if mode == "answer":
                draw_char_center(c, ch, x, y_box, CELL, font_name, BODY_FONT)

            x += (CELL + GAP_X)

        # 每句结束换行
        y -= (CELL + LINE_GAP)

    return y


# -----------------------------
# JSON 读取
# -----------------------------
def load_items(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    raise ValueError("JSON结构不正确：需要是数组，或 {\"items\":[...]} 格式")


# -----------------------------
# PDF 生成
# -----------------------------
def make_pdf(items: List[Dict[str, Any]], out_path: str, mode: str):
    font_name = register_cjk_font()

    page_title = "田字格默写练习" if mode == "practice" else "田字格默写答案"
    c = canvas.Canvas(out_path, pagesize=A4)

    # 第一页页眉
    c.setFont(font_name, 10)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 8 * mm, page_title)

    y = PAGE_H - MARGIN_TOP

    for idx, it in enumerate(items, start=1):
        title = (it.get("title") or "").strip()
        author = (it.get("author") or "").strip()
        dynasty = (it.get("dynasty") or "").strip()
        content = (it.get("content") or "").strip()

        # 每篇开始前确保空间
        y = ensure_space(c, font_name, page_title, y, need_h=30 * mm)

        # 标题块
        y = draw_section_header(c, idx, title, author, mode, font_name, y,dynasty)

        # 正文田字格
        y = render_text_as_tianzige(c, content, mode, font_name, page_title, y)

        # 篇与篇之间再留一点空
        y -= 4 * mm

        # 太靠底就换页
        y = ensure_space(c, font_name, page_title, y, need_h=20 * mm)

    c.save()
    print(f"[OK] {mode} -> {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="poems_27.json")
    ap.add_argument("--practice_out", required=True, help="练习版PDF输出")
    ap.add_argument("--answer_out", required=True, help="答案版PDF输出")
    args = ap.parse_args()

    items = load_items(args.input)

    make_pdf(items, args.practice_out, mode="practice")
    make_pdf(items, args.answer_out, mode="answer")


if __name__ == "__main__":
    main()

