
import sys
import os
from db import init_db_pool
from flask_cors import CORS
from flask import Flask, request, send_from_directory

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BaseConfig
import logging
from logging_config import setup_logging

# 导入蓝图
from routes.spellingbee_routes import spellingbee_bp
from routes.auth_routes import auth_bp

# 前端构建产物路径
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'dist')

def create_app(config_class=None):
    """创建应用，支持测试配置"""
    app = Flask(__name__)
    
    # 1. 首先加载配置类
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(BaseConfig)
    
    setup_logging(app)

    # 初始化数据库
    init_db_pool(app.config)

    # 启用CORS
    CORS(app, resources={r"/france/api/*": {"origins": "*"}})

    # 注册API蓝图（带/france前缀）
    blueprints = [
        (auth_bp, '/france/api/auth'),
        (spellingbee_bp, '/france/api/spellingbee'),
    ]
    
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
    
    # 健康检查
    @app.route('/france/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'service': 'franchstudy'}
    
    # 前端静态文件
    @app.route('/france/<path:path>')
    def serve_frontend(path):
        if path.startswith('api/') or path.startswith('health'):
            # API路由已由蓝图中处理，不会到这里
            return {'error': 'not found'}, 404
        file_path = os.path.join(FRONTEND_DIST, path)
        if os.path.isfile(file_path):
            return send_from_directory(FRONTEND_DIST, path)
        return send_from_directory(FRONTEND_DIST, 'index.html')
    
    @app.route('/france/')
    def serve_index():
        return send_from_directory(FRONTEND_DIST, 'index.html')
    
    # 添加请求日志
    @app.before_request
    def log_request_info():
        app.logger.info('请求: %s %s', request.method, request.url)
    
    @app.after_request
    def log_response_info(response):
        app.logger.info('响应: %s %s - %s', request.method, request.url, response.status)
        return response

    @app.errorhandler(404)
    def not_found(error):
        return {'error': '请求的资源不存在'}, 404
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error('未处理的异常: %s', str(e), exc_info=True)
        return {"error": "服务器内部错误"}, 500
    
    return app

# 为了支持flask run命令
app = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    if debug:
        app.logger.setLevel(logging.DEBUG)

    app.logger.info(f'启动应用: host={host}, port={port}, debug={debug}')
    app.run(host=host, port=port, debug=debug)

