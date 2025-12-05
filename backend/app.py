# backend/app.py
import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # 按你实际的DeepSeek API改

def call_deepseek(messages):
    """
    调用 DeepSeek 大模型的辅助函数。
    注意：下面这个请求格式只是“接近 OpenAI Chat API 的示例”，
    你需要根据 DeepSeek 官方文档调整 url / headers / body。
    """
    if not DEEPSEEK_API_KEY:
        # 开发阶段方便调试，可以先返回一个假数据
        return {
            "meaning": "【DEMO】这里是句子的中文大意。",
            "vocab": [],
            "grammar": "【DEMO】这里是语法说明。",
            "examples": [],
            "tips": "请配置 DEEPSEEK_API_KEY 才能真实调用模型。"
        }

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",  # 替换成你实际可用的模型名称
        "messages": messages,
        "temperature": 0.3
    }

    resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # 这里假设 DeepSeek 返回格式类似 OpenAI：
    content = data["choices"][0]["message"]["content"]

    # 让模型直接输出 JSON 字符串，我们再解析
    try:
        import json
        parsed = json.loads(content)
        return parsed
    except Exception:
        # 如果解析失败，就当成纯文本包一下
        return {
            "raw": content
        }


@app.route("/api/explain", methods=["POST"])
def explain_sentence():
    """
    输入：
    {
      "lesson_title": "Rester ou partir ?",
      "sentence_id": "D10",
      "french_text": "Si vous faites du ski, j’en ferai aussi. Je suis assez grand maintenant !",
      "chinese_hint": "如果你们去滑雪，我也要去。我现在年纪已经够大了！",  # 可选
      "question": "这句话什么意思？帮我讲讲语法，用适合初二学生的中文。"
    }
    输出：
    {
      "ok": true,
      "data": {
        "meaning": "...",
        "vocab": [...],
        "grammar": "...",
        "examples": [...],
        "tips": "..."
      }
    }
    """
    data = request.get_json(force=True) or {}
    lesson_title = data.get("lesson_title", "")
    sentence_id = data.get("sentence_id", "")
    french_text = data.get("french_text", "")
    chinese_hint = data.get("chinese_hint", "")
    user_question = data.get("question", "")

    if not french_text:
        return jsonify({"ok": False, "error": "french_text 不能为空"}), 400

    # 构造发给 DeepSeek 的 messages
    system_prompt = """
你是一名用中文给初二学生讲解法语的老师。
学生使用的教材是《北外法语 马晓宏 第二册》，水平偏弱，目标是能听懂课文、通过校内考试。

请你对给出的这句法语做【结构化讲解】，要求输出 JSON 格式，不要多余文字：
{
  "meaning": "用简单中文写出整句大意",
  "vocab": [
    { "word": "...", "explain": "中文解释 + 词性 + 简单例子（如果需要）" }
  ],
  "grammar": "用初二能听懂的语言，解释这句中涉及的语法点（如将来时、si句型、tout用法等）",
  "examples": [
    { "french": "另一句类似结构的例句", "chinese": "对应中文" }
  ],
  "tips": "1~2条学习建议，比如怎么记、容易错在哪里"
}

注意：
- 用简体中文解释；
- 语法说明尽量口语化、举例子，不要讲专业术语。
"""

    user_content = f"""
课文标题：{lesson_title}
句子ID：{sentence_id}

法语原句：
{french_text}

（如果有）课本上的中文大意：
{chinese_hint}

学生的问题：
{user_question or "请帮我讲懂这句话，包括词汇和语法。"}
"""

    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_content.strip()}
    ]

    result = call_deepseek(messages)

    return jsonify({"ok": True, "data": result})


if __name__ == "__main__":
    # 开发环境直接运行
    app.run(host="0.0.0.0", port=5000, debug=True)

