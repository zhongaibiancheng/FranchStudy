import re
from psycopg2.extras import RealDictCursor
from db import init_db_pool, get_db
from flask import Flask
from config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)
init_db_pool(app.config)

# =========================
# 小工具：从 part_of_speech 推断名词性数
# =========================
def infer_from_pos(pos: str):
    """
    返回 (gender, number)
    - gender: 'm'/'f'/None
    - number: 'sg'/'pl'/None
    """
    if not pos:
        return (None, None)

    p = pos.strip().lower()

    # 名词：n.m. / n.f. / n.pl. / n.f.pl. / n.m.pl.
    if p.startswith("n."):
        gender = None
        number = None
        if ".m" in p:
            gender = "m"
        elif ".f" in p:
            gender = "f"

        # pl / sg
        if "pl" in p:
            number = "pl"
        else:
            number = "sg"
        return (gender, number)

    # 其它（a./adv./prép./conj./v. 等），这里不强行给 gender/number
    return (None, None)


# =========================
# 小工具：对形容词/分词类从 lemma 推断阴阳性
# =========================
FEMININE_SUFFIXES = (
    "e", "ée", "te", "se", "ne", "que", "che", "ge", "lle", "nne"
)

def guess_adj_gender(lemma: str, form: str):
    """
    很粗但实用：
    - form == lemma -> 视为阳性
    - form != lemma 且以常见阴性后缀结尾 -> 阴性
    否则返回 None
    """
    if not lemma or not form:
        return None
    if form == lemma:
        return "m"

    # 常见：petit->petite, pressé->pressée, exact->exacte, gentil->gentille...
    for suf in FEMININE_SUFFIXES:
        if form.endswith(suf) and len(form) >= len(lemma):
            return "f"
    return None


def guess_plural(lemma: str, form: str):
    """
    如果你拆出了明显复数变体（journaux/yeux 等），尽量标 pl：
    - form != lemma 且 (form 以 s/x 结尾) -> 倾向 pl
    仍然只是启发式；对不规则复数我们建议 mapping 显式标注。
    """
    if not lemma or not form:
        return None
    if form == lemma:
        return "sg"
    if form.endswith("s") or form.endswith("x"):
        return "pl"
    return None


# =========================
# mapping：允许每个 variant 带 meta（可选）
# 例如：
# "variants": [{"form":"entrez","meta":{"gram_mood":"imp","gram_person":"2p"}}]
# 也兼容原来的 ["a","b"] 写法
# =========================
mapping = [
  {"french_raw": "enchanté, e", "lemma": "enchanté", "variants": ["enchanté", "enchantée"]},
  {"french_raw": "étudiant, e", "lemma": "étudiant", "variants": ["étudiant", "étudiante"]},
  {"french_raw": "demi, e", "lemma": "demi", "variants": ["demi", "demie"]},
  {"french_raw": "pressé, e", "lemma": "pressé", "variants": ["pressé", "pressée"]},
  {"french_raw": "quel, quelle", "lemma": "quel", "variants": ["quel", "quelle"]},
  {"french_raw": "ami, e", "lemma": "ami", "variants": ["ami", "amie"]},
  {"french_raw": "beau (bel, belle)", "lemma": "beau", "variants": ["beau", "bel", "belle"]},
  {"french_raw": "français, e", "lemma": "français", "variants": ["français", "française"]},
  {"french_raw": "heureux, se", "lemma": "heureux", "variants": ["heureux", "heureuse"]},
  {"french_raw": "journal (pl. journaux)", "lemma": "journal", "variants": ["journal", "journaux"]},
  {"french_raw": "blanc, blanche", "lemma": "blanc", "variants": ["blanc", "blanche"]},
  {"french_raw": "frais, fraîche", "lemma": "frais", "variants": ["frais", "fraîche"]},
  {"french_raw": "joli, e", "lemma": "joli", "variants": ["joli", "jolie"]},
  {"french_raw": "vrai, e", "lemma": "vrai", "variants": ["vrai", "vraie"]},
  {"french_raw": "ce (cet), cette", "lemma": "ce", "variants": ["ce", "cet", "cette"]},
  {"french_raw": "gentil, le", "lemma": "gentil", "variants": ["gentil", "gentille"]},
  {"french_raw": "technicien, ne", "lemma": "technicien", "variants": ["technicien", "technicienne"]},
  {"french_raw": "chinois, e", "lemma": "chinois", "variants": ["chinois", "chinoise"]},
  {"french_raw": "désolé, e", "lemma": "désolé", "variants": ["désolé", "désolée"]},
  {"french_raw": "vingt et un/une", "lemma": "vingt et un", "variants": ["vingt et un", "vingt et une"]},
  {"french_raw": "trente et un / une", "lemma": "trente et un", "variants": ["trente et un", "trente et une"]},
  {"french_raw": "quarante et un / une", "lemma": "quarante et un", "variants": ["quarante et un", "quarante et une"]},
  {"french_raw": "cinquante et un / une", "lemma": "cinquante et un", "variants": ["cinquante et un", "cinquante et une"]},
  {"french_raw": "soixante et un / une", "lemma": "soixante et un", "variants": ["soixante et un", "soixante et une"]},
  {"french_raw": "un / une", "lemma": "un", "variants": ["un", "une"]},
  {"french_raw": "j'apprendre", "lemma": "apprendre", "variants": ["apprendre"]},
  {"french_raw": "charmant, e", "lemma": "charmant", "variants": ["charmant", "charmante"]},
  {"french_raw": "étranger, ère", "lemma": "étranger", "variants": ["étranger", "étrangère"]},
  {"french_raw": "exact, e", "lemma": "exact", "variants": ["exact", "exacte"]},
  {"french_raw": "petit, e", "lemma": "petit", "variants": ["petit", "petite"]},
  {"french_raw": "premier, ère", "lemma": "premier", "variants": ["premier", "première"]},
  {"french_raw": "entendu, e", "lemma": "entendu", "variants": ["entendu", "entendue"]},
  {"french_raw": "important, e", "lemma": "important", "variants": ["important", "importante"]},
  {"french_raw": "prochain, e", "lemma": "prochain", "variants": ["prochain", "prochaine"]},
  {"french_raw": "assis, e", "lemma": "assis", "variants": ["assis", "assise"]},
  {"french_raw": "compliqué, e", "lemma": "compliqué", "variants": ["compliqué", "compliquée"]},
  {"french_raw": "connu, e", "lemma": "connu", "variants": ["connu", "connue"]},
  {"french_raw": "fameux, se", "lemma": "fameux", "variants": ["fameux", "fameuse"]},
  {"french_raw": "O.K., OK", "lemma": "OK", "variants": ["OK", "O.K."]},
  {"french_raw": "directeur, trice", "lemma": "directeur", "variants": ["directeur", "directrice"]},
  {"french_raw": "froid, e", "lemma": "froid", "variants": ["froid", "froide"]},
  {"french_raw": "habiller (s')", "lemma": "s'habiller", "variants": ["s'habiller"]},
  {"french_raw": "laver (se)", "lemma": "se laver", "variants": ["se laver"]},
  {"french_raw": "lever (se)", "lemma": "se lever", "variants": ["se lever"]},
  {"french_raw": "loin de", "lemma": "loin de", "variants": ["loin de"]},
  {"french_raw": "pétrolier, ère", "lemma": "pétrolier", "variants": ["pétrolier", "pétrolière"]},
  {"french_raw": "promener(se)", "lemma": "se promener", "variants": ["se promener"]},
  {"french_raw": "regarder(se)", "lemma": "se regarder", "variants": ["se regarder"]},
  {"french_raw": "rencontrer(se)", "lemma": "se rencontrer", "variants": ["se rencontrer"]},
  {"french_raw": "œil (pl. yeux)", "lemma": "œil", "variants": ["œil", "yeux"]},
  {"french_raw": "entrez", "lemma": "entrer", "variants": ["entrer", "entrez"]},
  {"french_raw": "amusant, e", "lemma": "amusant", "variants": ["amusant", "amusante"]},
  {"french_raw": "faux, fausse", "lemma": "faux", "variants": ["faux", "fausse"]},
  {"french_raw": "gris, e", "lemma": "gris", "variants": ["gris", "grise"]},
  {"french_raw": "marqué, e", "lemma": "marqué", "variants": ["marqué", "marquée"]},
  {"french_raw": "pareil, le", "lemma": "pareil", "variants": ["pareil", "pareille"]},
  {"french_raw": "roux, rousse", "lemma": "roux", "variants": ["roux", "rousse"]},
  {"french_raw": "tempéré, e", "lemma": "tempéré", "variants": ["tempéré", "tempérée"]},
  {"french_raw": "haut, e", "lemma": "haut", "variants": ["haut", "haute"]},
  {"french_raw": "clair, e", "lemma": "clair", "variants": ["clair", "claire"]},
  {"french_raw": "commun, e", "lemma": "commun", "variants": ["commun", "commune"]},
  {"french_raw": "ennuyeux, se", "lemma": "ennuyeux", "variants": ["ennuyeux", "ennuyeuse"]},
  {"french_raw": "meublé, e", "lemma": "meublé", "variants": ["meublé", "meublée"]},
  {"french_raw": "rangé, e", "lemma": "rangé", "variants": ["rangé", "rangée"]},
  {"french_raw": "seul, e", "lemma": "seul", "variants": ["seul", "seule"]},
  {"french_raw": "tout, e", "lemma": "tout", "variants": ["tout", "toute"]},
  {"french_raw": "asseoir (s')", "lemma": "s'asseoir", "variants": ["s'asseoir"]},
]


def normalize_variants(variants):
    """
    把 variants 统一成:
    [{"form": "...", "meta": {...}}, ...]
    """
    out = []
    for v in variants:
        if isinstance(v, str):
            out.append({"form": v, "meta": {}})
        elif isinstance(v, dict) and "form" in v:
            out.append({"form": v["form"], "meta": v.get("meta", {}) or {}})
        else:
            raise ValueError(f"Invalid variant item: {v}")
    return out


def build_gram_fields(row: dict, lemma: str, form: str, variant_meta: dict):
    """
    根据原行的 part_of_speech + (lemma, form) + variant_meta 生成 gram_* 字段。
    variant_meta 的优先级最高。
    """
    pos = row.get("part_of_speech") or ""
    pos_l = pos.strip().lower()

    gram_gender = None
    gram_number = None
    gram_mood = None
    gram_person = None
    gram_tense = None

    # 1) 先从词性推断（名词最靠谱）
    g0, n0 = infer_from_pos(pos)
    gram_gender = g0
    gram_number = n0

    # 2) 形容词/分词类：a.
    if pos_l.startswith("a."):
        gg = guess_adj_gender(lemma, form)
        if gg:
            gram_gender = gg
        nn = guess_plural(lemma, form)
        if nn:
            gram_number = nn
        else:
            gram_number = gram_number or "sg"

    # 3) 数词、介词、副词等：不强行写 gender/number

    # 4) 动词：命令式等靠 meta 最稳
    # 也可以你未来扩展 gram_tense 等
    if pos_l.startswith("v."):
        # 默认不写 gender/number
        gram_gender = None
        gram_number = None

    # 5) variant_meta 覆盖一切
    if variant_meta:
        gram_gender = variant_meta.get("gram_gender", gram_gender)
        gram_number = variant_meta.get("gram_number", gram_number)
        gram_mood   = variant_meta.get("gram_mood", gram_mood)
        gram_person = variant_meta.get("gram_person", gram_person)
        gram_tense  = variant_meta.get("gram_tense", gram_tense)

    return gram_gender, gram_number, gram_mood, gram_person, gram_tense


# =========================
# 主流程：chaifen
# =========================
def chaifen(book: int, lesson: int, *, dry_run: bool = True):
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                for ele in mapping:
                    cur.execute(
                        "SELECT * FROM words WHERE book=%s AND french=%s ORDER BY id ASC",
                        (book, ele["french_raw"])
                    )
                    row = cur.fetchone()
                    if not row:
                        print(f"[SKIP] not found in DB: {ele['french_raw']}")
                        continue

                    wid = row["id"]
                    raw = row["french"]  # 原 french（此时等于 french_raw）
                    group_id = wid

                    variants = normalize_variants(ele["variants"])
                    first = variants[0]["form"]
                    lemma = ele["lemma"]

                    # 计算第一个变体的 gram_*
                    g, n, mood, person, tense = build_gram_fields(row, lemma, first, variants[0]["meta"])

                    # 1) 更新原记录：变成 variants[0]
                    cur.execute(
                        """
                        UPDATE words
                        SET french_raw=%s,
                            french=%s,
                            lemma=%s,
                            variant_group_id=%s,
                            gram_gender=%s,
                            gram_number=%s,
                            gram_mood=%s,
                            gram_person=%s,
                            gram_tense=%s
                        WHERE id=%s
                        """,
                        (raw, first, lemma, group_id, g, n, mood, person, tense, wid),
                    )
                    print(raw, "->", first)

                    # 2) 插入其余变体
                    for item in variants[1:]:
                        form = item["form"]
                        meta = item["meta"]

                        g, n, mood, person, tense = build_gram_fields(row, lemma, form, meta)

                        cur.execute(
                            """
                            INSERT INTO words
                                (book, lesson, french, chinese, part_of_speech, part_of_speech_full_chinese,
                                 french_raw, lemma, variant_group_id,
                                 gram_gender, gram_number, gram_mood, gram_person, gram_tense)
                            VALUES
                                (%s, %s, %s, %s, %s, %s,
                                 %s, %s, %s,
                                 %s, %s, %s, %s, %s)
                            """,
                            (
                                row["book"],
                                row["lesson"],
                                form,
                                row["chinese"],
                                row["part_of_speech"],
                                row["part_of_speech_full_chinese"],
                                raw,
                                lemma,
                                group_id,
                                g, n, mood, person, tense
                            ),
                        )
                        print(raw, "->", form)

                if dry_run:
                    conn.rollback()
                    print("[DRY RUN] rolled back.")
                else:
                    conn.commit()
                    print("[COMMIT] done.")
            except Exception as e:
                conn.rollback()
                raise


if __name__ == "__main__":
    # chaifen(1, 1, dry_run=True)
    chaifen(1, 1, dry_run=False)