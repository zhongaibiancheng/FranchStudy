# routes/auth.py
from flask import Blueprint, request, jsonify, current_app,g
from datetime import datetime, timedelta

import json
import time, random, string

import uuid
import re

from psycopg2.extras import RealDictCursor
from db import get_db

spellingbee_bp = Blueprint('speelingbee', __name__)

# 所有 API 路由都需要认证
from middleware.auth import token_required

@spellingbee_bp.before_request
@token_required
def before_api_request():
    # 这个函数会在每个 API 请求前执行，通过 token_required 进行认证
    pass

def _gram_label_cn(row: dict) -> str:
    """
    把 gram_* 字段拼成 UI 可展示的中文标签
    """
    gender = row.get("gram_gender")
    number = row.get("gram_number")
    mood = row.get("gram_mood")
    person = row.get("gram_person")

    parts = []

    # 命令式优先展示（尤其是 entrez 这种）
    if mood == "imp":
        # 2p = vous，2s = tu，1p = nous（如果未来你也会用到）
        person_map = {"2p": "vous(2p)", "2s": "tu(2s)", "1p": "nous(1p)"}
        parts.append(f"命令式·{person_map.get(person, person or '')}".rstrip("·"))
        return "；".join([p for p in parts if p])

    # 否则展示阴阳性、单复数
    if gender in ("m", "f"):
        parts.append("阳性" if gender == "m" else "阴性")

    if number in ("sg", "pl"):
        parts.append("单数" if number == "sg" else "复数")

    return "·".join(parts) if parts else ""


def _decorate_words(words: list[dict]) -> list[dict]:
    """
    给每个 word 增加 UI 友好字段
    """
    for w in words:
        w["pos_label_cn"] = w.get("part_of_speech_full_chinese") or w.get("part_of_speech") or ""
        w["gram_label_cn"] = _gram_label_cn(w)

        if w["pos_label_cn"] and w["gram_label_cn"]:
            w["display_label_cn"] = f'{w["pos_label_cn"]}｜{w["gram_label_cn"]}'
        else:
            w["display_label_cn"] = w["pos_label_cn"] or w["gram_label_cn"] or ""

    return words


# 听写内容创建
@spellingbee_bp.route('/exercise', methods=['POST'])
def create_exercise():
    current_app.logger.info('创建练习')

    if not request.data:
        current_app.logger.warning('请求体为空')
        return jsonify({'error': '请求体不能为空'}), 400

    try:
        data = request.get_json(force=True, silent=False)
    except Exception as e:
        current_app.logger.warning(f'JSON 解析失败: {str(e)}')
        return jsonify({'error': '请求数据格式错误，必须是有效的 JSON'}), 400

    if data is None:
        current_app.logger.warning('无效的 JSON 格式')
        return jsonify({'error': '请求数据格式错误，必须是有效的 JSON'}), 400

    if 'mode' not in data or 'count' not in data:
        return jsonify({'error': '缺少字段 mode 或 count'}), 400

    mode_str = data.get('mode')
    count = data.get('count')

    if mode_str not in ('lesson', 'wrongbook'):
        return jsonify({'error': 'mode 只能是 lesson 或 wrongbook'}), 400

    if mode_str == 'lesson':
        if 'book' not in data or 'lesson' not in data:
            return jsonify({'error': '缺少字段 book 或 lesson'}), 400

    book = data.get('book')
    lesson = data.get('lesson')

    # 0: 单词表 1: 错题本
    mode = 0 if mode_str == 'lesson' else 1
    user_id = g.current_user['id']

    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                if mode == 0:
                    sql = """
                        SELECT 
                            w.id AS word_id,
                            w.book,
                            w.lesson,
                            w.french,
                            w.chinese,
                            w.part_of_speech,
                            w.part_of_speech_full_chinese,
                            w.french_raw,
                            w.lemma,
                            w.variant_group_id,
                            w.gram_gender,
                            w.gram_number,
                            w.gram_mood,
                            w.gram_person,
                            w.gram_tense
                        FROM words AS w
                        LEFT JOIN exercise_words AS wp
                            ON wp.word_id = w.id
                            AND wp.user_id = %s
                        WHERE 
                            w.book = %s
                            AND w.lesson = %s
                            AND (wp.word_id IS NULL OR wp.finished = false)
                        ORDER BY random()
                        LIMIT %s;
                    """
                    cur.execute(sql, (user_id, book, lesson, count))
                    words = cur.fetchall()

                else:
                    sql = """
                        SELECT 
                            w.id AS word_id,
                            w.book,
                            w.lesson,
                            w.french,
                            w.chinese,
                            w.part_of_speech,
                            w.part_of_speech_full_chinese,
                            w.french_raw,
                            w.lemma,
                            w.variant_group_id,
                            w.gram_gender,
                            w.gram_number,
                            w.gram_mood,
                            w.gram_person,
                            w.gram_tense
                        FROM words AS w
                        INNER JOIN mistake_notebook AS wp
                            ON wp.word_id = w.id
                            AND wp.user_id = %s
                            AND wp.wrong_count >= wp.right_count
                        ORDER BY random()
                        LIMIT %s;
                    """
                    cur.execute(sql, (user_id, count))
                    words = cur.fetchall()

                # 把单词插入到 exercise_words
                insert_sql = """
                    INSERT INTO exercise_words(user_id, word_id, created_at)
                    VALUES (%s, %s, now())
                    RETURNING id
                """
                for w in words:
                    cur.execute(insert_sql, (user_id, w["word_id"]))
                    w["exercise_id"] = cur.fetchone()["id"]

                # 追加 UI 展示字段
                words = _decorate_words(words)

                conn.commit()
                return jsonify({
                    'success': True,
                    'message': '创建练习成功',
                    'words': words
                })

            except Exception as e:
                conn.rollback()
                current_app.logger.error(f'创建练习过程中发生错误: {str(e)}', exc_info=True)
                return jsonify({'error': '服务器内部错误'}), 500
            
@spellingbee_bp.route('/exercise/<int:id>', methods=['PUT'])
def update_exercise(id: int):
    current_app.logger.info('更新听写结果')

    data = request.get_json(silent=True)
    if data is None:
        current_app.logger.warning('更新听写结果失败：请求体不是有效 JSON')
        return jsonify({'error': '请求数据格式错误，必须是有效的 JSON'}), 400

    if 'result' not in data or 'word_id' not in data:
        return jsonify({'error': '缺少字段 result 或者 word_id'}), 400

    try:
        result = int(data.get('result'))
    except (TypeError, ValueError):
        return jsonify({'error': 'result 必须是数字 0 或 1'}), 400

    # 只允许 0/1
    if result not in (0, 1):
        return jsonify({'error': 'result 只能是 0(错) 或 1(对)'}), 400

    try:
        word_id = int(data.get('word_id'))
    except (TypeError, ValueError):
        return jsonify({'error': 'word_id 必须是数字'}), 400

    try:
        user_id = g.current_user['id']
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                sql = """
                    UPDATE exercise_words
                    SET result = %s,finished=true
                    WHERE id = %s
                """
                cur.execute(sql, (result, id))

                if cur.rowcount == 0:
                    return jsonify({'error': f'id={id} 不存在'}), 404
                
                if result == 0:#错误的时候 登陆 错题本
                    sql = "update mistake_notebook set wrong_count = wrong_count+1 where word_id=%s and user_id = %s"
                    cur.execute(sql, (word_id,user_id))
                    
                    if cur.rowcount == 0:
                        sql = "insert into mistake_notebook(word_id,user_id) values(%s,%s)"
                        cur.execute(sql, (word_id,user_id))
                else:#正确的时候需要更新 错题本
                     sql = "update mistake_notebook set right_count = right_count+1 where word_id=%s and user_id = %s"
                     cur.execute(sql, (word_id,user_id))
        return jsonify({'success': True, 'message': '听写结果更新成功'}), 200

    except Exception as e:
        current_app.logger.error(f'更新听写结果发生错误: {str(e)}', exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500