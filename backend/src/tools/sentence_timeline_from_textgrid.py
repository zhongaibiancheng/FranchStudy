# sentence_timeline_from_textgrid.py
from pathlib import Path
from praatio import textgrid
from rapidfuzz import fuzz
import re, json

def norm(s: str):
    s = s.lower()
    s = re.sub(r"[’']", "'", s)
    s = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ' -]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def load_words(tg_path: Path, tier_name_guess=("words", "Word", "words - speaker1")):
    tg = textgrid.openTextgrid(tg_path, includeEmptyIntervals=False)
    # 找一个最像“词层”的 tier
    tier = None
    for name in tg.tierNames:
        if any(k.lower() in name.lower() for k in tier_name_guess):
            tier = tg.getTier(name)
            break
    if tier is None:
        # 兜底：拿第一个 IntervalTier
        tier = tg.tiers[0]

    words = []
    for itv in tier.entries:
        w = itv.label.strip()
        if not w:
            continue
        words.append({"word": w, "start": itv.start, "end": itv.end})
    return words

def align_sentences(words, sentences):
    # 简单顺序贪心：用滑窗找最像的一段词
    w_tokens = [norm(w["word"]) for w in words]

    results = []
    p = 0
    for s in sentences:
        s_norm = norm(s)
        s_toks = s_norm.split()
        if not s_toks:
            results.append({"text": s, "start": None, "end": None, "score": 0})
            continue

        # 估计窗口长度
        L = len(s_toks)
        min_len = max(1, int(L * 0.6))
        max_len = max(min_len, int(L * 1.6))

        best = (0, None, None)
        # 从当前位置开始往后搜索一段范围
        search_end = min(len(w_tokens), p + max_len + 40)

        for i in range(p, search_end):
            for j in range(i + min_len, min(search_end, i + max_len) + 1):
                cand = " ".join(w_tokens[i:j])
                score = fuzz.token_set_ratio(s_norm, cand)
                if score > best[0]:
                    best = (score, i, j)

        score, i, j = best
        if i is None:
            results.append({"text": s, "start": None, "end": None, "score": 0})
            continue

        start = words[i]["start"]
        end = words[j-1]["end"]
        results.append({"text": s, "start": start, "end": end, "score": score})
        p = j  # 指针前移（保持顺序）

    return results

def load_sentences_txt(path: str):
    with open(path, "r", encoding="utf-8") as f:
        # 去空行、去首尾空白
        return [line.strip() for line in f if line.strip()]
    
if __name__ == "__main__":
    tg_path = Path("output/lesson_01.TextGrid")
    # sentences = json.load(open("sentences.json", "r", encoding="utf-8"))  # 你的句子数组
    sentences = load_sentences_txt("lesson_01.txt")

    words = load_words(tg_path)
    aligned = align_sentences(words, sentences)

    json.dump(aligned, open("sentence_timeline.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("OK -> sentence_timeline.json")
