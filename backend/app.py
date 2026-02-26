
import sys
import os
import subprocess
from db import init_db_pool
from flask_cors import CORS
from flask import Flask, request

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BaseConfig
import logging
from logging_config import setup_logging

# 导入蓝图
from routes.spellingbee_routes import spellingbee_bp
from routes.auth_routes import auth_bp

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
    # ⭐ 只初始化一次
    init_db_pool(app.config)

    # 启用CORS，允许所有来源
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 一次性注册所有蓝图
    blueprints = [
        (auth_bp, '/api/auth'),
        (spellingbee_bp, '/api/spellingbee'),
    ]
    
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
    
    # 添加请求日志
    @app.before_request
    def log_request_info():
        app.logger.info('请求: %s %s', request.method, request.url)
    
    @app.after_request
    def log_response_info(response):
        app.logger.info('响应: %s %s - %s', request.method, request.url, response.status)
        return response
    
    # 添加错误处理日志
    # @user_bp.errorhandler(404)

    
    @app.errorhandler(Exception)
    def not_found(error):
        print("请求的资源不存在请求的资源不存在请求的资源不存在请求的资源不存在")
        return {'error': '请求的资源不存在'}, 404
    
    def handle_exception(e):
        app.logger.error('未处理的异常: %s', str(e), exc_info=True)
        return {"error": "服务器内部错误"}, 500
    
    # 健康检查路由
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'service': 'quiz-platform-api'}
    
    return app

# 为了支持flask run命令
app = create_app()

if __name__ == '__main__':
    # 获取主机和端口配置
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # 在调试模式下也启用日志
    if debug:
        app.logger.setLevel(logging.DEBUG)
        app.logger.debug('应用在调试模式下启动')

    app.logger.info(f'启动应用: host={host}, port={port}, debug={debug}')
    app.run(host=host, port=port, debug=debug)

