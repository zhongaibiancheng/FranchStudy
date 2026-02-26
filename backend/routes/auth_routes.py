# routes/auth.py
from flask import Blueprint, request, jsonify, current_app
import jwt
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash,generate_password_hash

import json
import time, random, string

import uuid
import re

from psycopg2.extras import RealDictCursor
from db import get_db

auth_bp = Blueprint('auth', __name__)

# 用户注册
@auth_bp.route('/register', methods=['POST'])
def register():
    current_app.logger.info('收到注册请求')

    # 安全地获取 JSON 数据
    if not request.data:  # 检查是否有请求体
        current_app.logger.warning('注册失败：请求体为空')
        return jsonify({'error': '请求体不能为空'}), 400
    
    try:
        data = request.get_json(force=True, silent=False)  # 强制解析，不静默
    except Exception as e:
        current_app.logger.warning(f'JSON 解析失败: {str(e)}')
        return jsonify({'error': '请求数据格式错误，必须是有效的 JSON'}), 400
    
    # 如果 data 为 None，说明 JSON 解析失败
    if data is None:
        current_app.logger.warning('注册失败：无效的 JSON 格式')
        return jsonify({'error': '请求数据格式错误，必须是有效的 JSON'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    # 验证必要参数
    if not all([username, email, password]):
        current_app.logger.warning('注册失败：缺少必要参数')
        return jsonify({'error': '用户名、邮箱、密码不能为空'}), 400
    
    # 去除前后空格
    username = username.strip()
    email = email.strip()
    
    # 验证用户名长度
    if len(username) < 3:
        current_app.logger.warning(f'注册失败：用户名长度不足 - {username}')
        return jsonify({'error': '用户名长度不能少于3个字符'}), 400
    
    if len(username) > 20:
        current_app.logger.warning(f'注册失败：用户名长度超限 - {username}')
        return jsonify({'error': '用户名长度不能超过20个字符'}), 400
    
    # 验证用户名字符（允许字母、数字、下划线和中文）
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
        current_app.logger.warning(f'注册失败：用户名包含非法字符 - {username}')
        return jsonify({'error': '用户名只能包含字母、数字、下划线和中文字符'}), 400
    
    # 验证邮箱格式
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        current_app.logger.warning(f'注册失败：邮箱格式错误 - {email}')
        return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 验证邮箱长度
    if len(email) > 120:
        current_app.logger.warning(f'注册失败：邮箱长度超限 - {email}')
        return jsonify({'error': '邮箱长度不能超过120个字符'}), 400
    
    # 验证密码长度
    if len(password) < 6:
        current_app.logger.warning('注册失败：密码长度不足')
        return jsonify({'error': '密码长度不能少于6个字符'}), 400
    
    if len(password) > 20:
        current_app.logger.warning('注册失败：密码长度超限')
        return jsonify({'error': '密码长度不能超过20个字符'}), 400
    
    # 验证密码和确认密码是否一致
    # if password != confirm_password:
    #     current_app.logger.warning('注册失败：密码和确认密码不一致')
    #     return jsonify({'error': '密码和确认密码不一致'}), 400
    
    # 密码强度验证（可选）
    if not re.search(r'[A-Z]', password):  # 至少一个大写字母
        current_app.logger.warning('注册失败：密码强度不足，需要至少一个大写字母')
        return jsonify({'error': '密码必须包含至少一个大写字母'}), 400
    
    if not re.search(r'[a-z]', password):  # 至少一个小写字母
        current_app.logger.warning('注册失败：密码强度不足，需要至少一个小写字母')
        return jsonify({'error': '密码必须包含至少一个小写字母'}), 400
    
    if not re.search(r'[0-9]', password):  # 至少一个数字
        current_app.logger.warning('注册失败：密码强度不足，需要至少一个数字')
        return jsonify({'error': '密码必须包含至少一个数字'}), 400
    
    # # 检查用户名是否已存在
    # existing_user = User.query.filter_by(username=username).first()
    # if existing_user:
    #     current_app.logger.warning(f'注册失败：用户名已存在 - {username}')
    #     return jsonify({'error': '用户名已被占用'}), 409
    
    # # 检查邮箱是否已存在
    # existing_email = User.query.filter_by(email=email).first()
    # if existing_email:
    #     current_app.logger.warning(f'注册失败：邮箱已存在 - {email}')
    #     return jsonify({'error': '邮箱已被注册'}), 409
    
    # # 创建新用户
    # hashed_password = generate_password_hash(password)
    # new_user = User(
    #     username=username,
    #     email=email,
    #     password_hash=hashed_password,
    #     is_admin=False
    # )
    
    # db.session.add(new_user)
    # db.session.commit()
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                # 创建新用户
                hashed_password = generate_password_hash(password)
                sql = """
                        insert into users(
                            username, 
                            email, 
                            password_hash, 
                            is_admin, 
                            created_at)values(
                                '%s',
                                '%s',
                                '%s',
                                False,
                                now()
                            ) RETURNING id;
                """%(username,email,hashed_password)
                current_app.logger.info(f'用户注册sql: {sql}')
                cur.execute(sql)
                
                user  = cur.fetchone()
                conn.commit()
                
                current_app.logger.info(f'用户注册成功: {username} ({email})')
        
                # 生成 JWT token（可选，注册后自动登录）
                token = jwt.encode({
                    'user_id': user['id'],
                    'username': username,
                    'exp': datetime.utcnow() + timedelta(hours=24 * 7)
                }, current_app.config['SECRET_KEY'], algorithm='HS256')
                
                return jsonify({
                    'success': True,
                    'message': '注册成功',
                    'token': token,  # 可选，根据需求决定是否返回 token
                    # 'user':['username':username,'id':user['id']]
                }), 201
        
            except Exception as e:
                current_app.logger.error(f'注册过程中发生错误: {str(e)}', exc_info=True)
                return jsonify({'error': '服务器内部错误'}), 500
    
# 用户登录
@auth_bp.route('/login', methods=['POST'])
def login():

    current_app.logger.info('收到登录请求')

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
    
    username = data.get('username')
    password = data.get('password')
    
    # 验证必要参数
    if username is None or password is None:
        current_app.logger.warning('登录失败：缺少必要参数')
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    # 去除用户名前后空格
    username = username.strip()
    
    # 验证用户名长度
    if len(username) < 6:
        current_app.logger.warning(f'登录失败：用户名长度不足 - {username}')
        return jsonify({'error': '用户名长度不能少于3个字符'}), 400
    
    if len(username) > 20:
        current_app.logger.warning(f'登录失败：用户名长度超限 - {username}')
        return jsonify({'error': '用户名长度不能超过20个字符'}), 400
    
    # 验证用户名字符（允许字母、数字、下划线和中文）
    import re
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
        current_app.logger.warning(f'登录失败：用户名包含非法字符 - {username}')
        return jsonify({'error': '用户名只能包含字母、数字、下划线和中文字符'}), 400
    
    # 验证密码长度
    if len(password) < 6:
        current_app.logger.warning('登录失败：密码长度不足')
        return jsonify({'error': '密码长度不能少于6个字符'}), 400
    
    if len(password) > 20:
        current_app.logger.warning('登录失败：密码长度超限')
        return jsonify({'error': '密码长度不能超过20个字符'}), 400
    
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                # 创建新用户
                hashed_password = generate_password_hash(password)
                sql = """
                        select 
                            id,
                            username 
                        from 
                            uses 
                        where 
                            username='%s';
                """%(username)

                cur.execute(sql)
                
                user  = cur.fetchone()

                if not user or not user.check_password(password):
                    current_app.logger.warning(f'登录失败：用户名或密码错误 - {username}')
                    return jsonify({'error': '用户名或密码错误'}), 401
        
                # 生成 JWT token
                token = jwt.encode({
                    'user_id': user['id'],
                    'username': user['username'],
                    'exp': datetime.utcnow() + timedelta(hours=24*7)
                }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
                return jsonify({
                    'success': True,
                    'message': '登录成功',
                    'token': token,
                    'user': user.to_dict()
                })
            except Exception as e:
                current_app.logger.error(f'登录过程中发生错误: {str(e)}', exc_info=True)
                return jsonify({'error': '服务器内部错误'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # 前端删除 token 即可，服务端可以维护黑名单（可选）
    return jsonify({
        'success': True,
        'message': '退出成功'
    })