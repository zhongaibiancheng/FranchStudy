# middleware/auth.py
import jwt
from functools import wraps
from flask import request, jsonify, current_app,g
from datetime import datetime, timedelta

from psycopg2.extras import RealDictCursor
from db import get_db
def _get_auth_headers(user_id, username):
    """生成认证headers"""
    token = jwt.encode({
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() - timedelta(hours=24)
    }, 'test-secret-key-for-auth', algorithm='HS256')
    
    return {'Authorization': f'Bearer {token}'}
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 跳过 OPTIONS 预检请求
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
        
        # 打印所有请求头
        headers_dict = dict(request.headers)
        current_app.logger.info('所有请求头:')
        for key, value in headers_dict.items():
            current_app.logger.info(f'  {key}: {value}')
        
        token = None
        
        # 检查 Authorization 头
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                current_app.logger.info(f'提取的 token: {token}')
            else:
                current_app.logger.warning('Authorization 头格式不正确，缺少 Bearer 前缀')
        else:
            current_app.logger.warning('请求头中缺少 Authorization 字段')
        
        if not token:
            current_app.logger.error('未找到有效的 token')
            return jsonify({
                'success': False,
                'message': '访问令牌缺失'
            }), 401
        
        try:
            # token = _get_auth_headers(11,'tests')['Authorization'].split(' ')[1]
            current_app.logger.info(f"开始解码 token...{token}")
            # 解码 token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_app.logger.info(f'解码后的 token 数据: {data}')
            
            # 这里应该是你的用户查询逻辑
            with get_db() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    try:
                        sql = """
                            select * from users
                            where 
                            id = %d
                        """%(data['user_id'])
                        cur.execute(sql)
                        current_user = cur.fetchone()
                        
                        if current_user:
                            g.current_user = {
                                'id': current_user['id'],
                                'username': current_user['username'],
                                'is_admin':current_user['is_admin']
                            }
                        else:
                            return jsonify({
                                'success': False,
                                'message': '用户不存在'
                            }), 401
                    except Exception as e:
                        current_app.logger.error(f'Token 处理异常: {str(e)}')
                        return jsonify({
                            'success': False,
                            'message': '令牌验证失败'
                        }), 401
        except jwt.ExpiredSignatureError:
            current_app.logger.error('Token 已过期')
            return jsonify({
                'success': False,
                'message': '令牌已过期'
            }), 401
        except jwt.InvalidTokenError as e:
            current_app.logger.error(f'无效的 token: {str(e)}')
            return jsonify({
                'success': False,
                'message': '无效令牌'
            }), 401
        except Exception as e:
            current_app.logger.error(f'Token 处理异常: {str(e)}')
            return jsonify({
                'success': False,
                'message': '令牌验证失败'
            }), 401
        return f(*args, **kwargs)
    
    return decorated