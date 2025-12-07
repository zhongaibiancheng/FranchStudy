import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

from rapidfuzz import fuzz
import whisper_timestamped as wt


# ----------------------------
# 配置
# ----------------------------
AUDIO_DIR = Path("audios")
LESSON_JSON_DIR = Path("./data/lessons")
OUT_AUDIO_ROOT = Path("./output/audio")

LANG = "fr"
WHISPER_MODEL = "small"  # tiny / base / small / medium

LANG = "fr"
WHISPER_MODEL = "small"

# ✅ 建议：全局只加载一次
MODEL = wt.load_model(WHISPER_MODEL)  # 可加 device="cpu" 或 "cuda"

# ----------------------------
# 文本清洗
# ----------------------------
def norm_text(s: str) -> str:
    s = s or ""
    s = s.lower()
    s = re.sub(r"[’']", "'", s)
    s = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s'-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokenize(s: str) -> List[str]:
    s = norm_text(s)
    return [t for t in s.split(" ") if t]


# ----------------------------
# 从 whisper 结果抽取词级时间轴
# ----------------------------
def extract_words(result: Dict) -> List[Dict]:
    words = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            # w: {'text', 'start', 'end', ...}
            txt = (w.get("text") or "").strip()
            if not txt:
                continue
            words.append({
                "text": txt,
                "start": float(w.get("start", 0.0)),
                "end": float(w.get("end", 0.0)),
            })
    return words


# ----------------------------
# 句子到词序列的模糊匹配
#   - 用滑窗找最像的一段
# ----------------------------
def find_best_window(words: List[Dict], sentence: str) -> Tuple[float, int, int]:
    sent_tokens = tokenize(sentence)
    if not sent_tokens:
        return 0, -1, -1

    # 把识别词也做 normalize
    word_tokens = [norm_text(w["text"]) for w in words]

    n = len(word_tokens)
    m = len(sent_tokens)

    # 窗口长度允许一点浮动
    cand_lens = [max(1, m - 2), m - 1, m, m + 1, m + 2]

    best_score = 0.0
    best_i = -1
    best_j = -1

    sent_str = " ".join(sent_tokens)

    for L in cand_lens:
        if L <= 0:
            continue
        for i in range(0, n - L + 1):
            j = i + L
            win_str = " ".join(word_tokens[i:j])
            score = fuzz.token_set_ratio(sent_str, win_str)
            if score > best_score:
                best_score = score
                best_i, best_j = i, j

    return best_score, best_i, best_j


# ----------------------------
# 用 ffmpeg 切片
# ----------------------------
def cut_audio(in_audio: Path, out_audio: Path, start: float, end: float):
    out_audio.parent.mkdir(parents=True, exist_ok=True)

    # -ss 放前面是快切；精度够用
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(max(0, start)),
        "-to", str(max(0, end)),
        "-i", str(in_audio),
        "-c", "copy",
        str(out_audio)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ----------------------------
# 处理单课
# ----------------------------
def process_one_lesson(lesson_no: int):
    audio = AUDIO_DIR / f"lesson_{lesson_no:02d}.m4a"
    jpath = LESSON_JSON_DIR / f"lesson_{lesson_no:02d}.json"

    if not audio.exists():
        print(f"[SKIP] audio not found: {audio}")
        return
    if not jpath.exists():
        print(f"[SKIP] json not found: {jpath}")
        return

    data = json.loads(jpath.read_text(encoding="utf-8"))
    sentences = data.get("text", [])

    if not sentences:
        print(f"[SKIP] empty lesson json: {jpath}")
        return

    print(f"[ASR] lesson {lesson_no:02d} -> {audio.name}")
    # result = wt.transcribe(str(audio), language=LANG, model=WHISPER_MODEL)
    result = wt.transcribe(MODEL, str(audio), language=LANG)
    words = extract_words(result)

    if not words:
        print(f"[FAIL] no words recognized for lesson {lesson_no:02d}")
        return

    out_dir = OUT_AUDIO_ROOT / f"lesson_{lesson_no:02d}"

    # 按顺序匹配，确保时间单调递增（减少错配）
    cursor = 0

    for idx, item in enumerate(sentences):
        sent_text = item.get("french_full") or item.get("french_gap") or ""
        sid = item.get("id") or f"S{idx+1:02d}"

        # 只在 cursor 之后的词里找
        sub_words = words[cursor:]
        score, i, j = find_best_window(sub_words, sent_text)

        if i == -1:
            print(f"  [WARN] {sid} not matched")
            continue

        # 映射回全局索引
        i_global = cursor + i
        j_global = cursor + j

        # 简单阈值
        if score < 70:
            print(f"  [WARN] low score {score:.1f} for {sid}")
            # 仍然可尝试切，按需你可以选择 continue

        start = words[i_global]["start"]
        end = words[j_global - 1]["end"]

        out_audio = out_dir / f"{sid}.m4a"
        cut_audio(audio, out_audio, start, end)

        # 回写 JSON 字段
        item["audio"] = f"/audio/lesson_{lesson_no:02d}/{sid}.m4a"
        item["audio_start"] = start
        item["audio_end"] = end
        item["asr_match_score"] = score

        # 推进游标，减少下一句错配
        cursor = max(cursor, j_global)

        print(f"  [OK] {sid} score={score:.1f} -> {out_audio.name}")

    # 保存更新后的 JSON
    jpath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] updated {jpath}")


# ----------------------------
# 批量入口
# ----------------------------
def main():
    # 自动探测 lesson_XX 文件
    lesson_nos = []

    for p in sorted(AUDIO_DIR.glob("lesson_*.m4a")):
        m = re.search(r"lesson_(\d+)\.m4a$", p.name)
        if m:
            lesson_nos.append(int(m.group(1)))

    if not lesson_nos:
        print("[FAIL] no audios found in audios/")
        return

    for no in lesson_nos:
        try:
            process_one_lesson(no)
        except subprocess.CalledProcessError:
            print(f"[FAIL] ffmpeg slice failed for lesson {no:02d}")
        except Exception as e:
            print(f"[FAIL] lesson {no:02d}: {repr(e)}")


if __name__ == "__main__":
    main()
