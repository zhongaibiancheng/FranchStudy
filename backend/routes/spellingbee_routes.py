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

# 用户登录
@spellingbee_bp.route('/exercise', methods=['POST'])
def create_exercise():
    current_app.logger.info('创建练习')

    # 安全地获取 JSON 数据
    if not request.data:  # 检查是否有请求体
        current_app.logger.warning('登录失败：请求体为空')
        return jsonify({'error': '请求体不能为空'}), 400
    
    try:
        data = request.get_json(force=True, silent=False)  # 强制解析，不静默
    except Exception as e:
        current_app.logger.warning(f'JSON 解析失败: {str(e)}')
        return jsonify({'error': '请求数据格式错误，必须是有效的 JSON'}), 400
    
    # 如果 data 为 None，说明 JSON 解析失败
    if data is None:
        current_app.logger.warning('登录失败：无效的 JSON 格式')
        return jsonify({'error': '请求数据格式错误，必须是有效的 JSON'}), 400
    
    if 'mode' not in data:
        return jsonify({'error': '缺少字段 mode'}), 400
    mode = data.get('mode')
    if mode not in ('lesson', 'wrongbook'):
        return jsonify({'error': 'mode 只能是 lesson 或 wrongbook'}), 400
    
    if data.get('mode') == 'lesson':#单词表
        if 'book' not in data or 'lesson' not in data:
            return jsonify({'error': '缺少字段 book 或者 lesson'}), 400
    
    book = data.get('book')
    lesson = data.get('lesson')
    
    #0:单词表 1:错题本
    mode = 0 if data.get('mode')=='lesson' else 1
    
    user_id = g.current_user['id']
    
    current_app.logger.info(f'用户 {user_id} 请求创建练习，模式: {mode}, 书籍: {book}, 课程: {lesson}') 
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                if mode == 0: #单词表
                    sql = """
                            select 
                                w.id as word_id,
                                w.book,
                                w.lesson,
                                w.french, 
                                w.chinese, 
                                w.part_of_speech, 
                                w.part_of_speech_full_chinese  
                            from 
                                words as w LEFT JOIN exercise_words as wp
                                ON wp.word_id = w.id
                                AND wp.user_id = %s 
                            where 
                                book=%s and lesson = %s
                                AND (wp.word_id IS NULL or wp.finished = false)
                                ORDER BY random()
                                LIMIT %s;
                    """
                    cur.execute(sql,(user_id,book,lesson,10))
                    
                    words  = cur.fetchall()
            
                    #把单词插入到 exercise_words
                    sql = """
                        insert into
                            exercise_words(user_id,word_id,created_at)values(%s,%s,now()) RETURNING id
                    """
                    for word in words:
                        cur.execute(sql,(user_id,word['word_id']))
                        
                        exercise_id = cur.fetchone()['id']
                        word['exercise_id'] = exercise_id;
                    
                    return jsonify({
                        'success': True,
                        'message': '登录成功',
                        'words': words
                    })
                else:#错题本
                    sql = """
                            select 
                                w.id as word_id,
                                w.book,
                                w.lesson,
                                w.french, 
                                w.chinese, 
                                w.part_of_speech, 
                                w.part_of_speech_full_chinese  
                            from 
                                words as w INNER JOIN mistake_notebook as wp
                                ON wp.word_id = w.id
                                AND wp.user_id = %s
                                and wp.wrong_count >= wp.right_count
                                ORDER BY random()
                                LIMIT %s;
                    """
                    cur.execute(sql,(user_id,10))
                    
                    words  = cur.fetchall()
            
                    #把单词插入到 exercise_words
                    sql = """
                        insert into
                            exercise_words(user_id,word_id,created_at)values(%s,%s,now()) RETURNING id
                    """
                    for word in words:
                        cur.execute(sql,(user_id,word['word_id']))
                        
                        exercise_id = cur.fetchone()['id']
                        word['exercise_id'] = exercise_id;
                    
                    return jsonify({
                        'success': True,
                        'message': '登录成功',
                        'words': words
                    })
            except Exception as e:
                current_app.logger.error(f'登录过程中发生错误: {str(e)}', exc_info=True)
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