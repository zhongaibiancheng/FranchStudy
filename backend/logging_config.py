import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    try:
        # 获取日志目录
        base_path = os.environ.get('LOG_BASE_DIR', '../logs')
        
        # 确保目录存在
        os.makedirs(base_path, mode=0o755, exist_ok=True)
        
        # 跨平台权限检查
        if hasattr(os, 'geteuid'):  # Linux/Unix系统
            import pwd, grp
            appuser_uid = pwd.getpwnam('appuser').pw_uid
            appuser_gid = grp.getgrnam('appuser').gr_gid
            os.chown(base_path, appuser_uid, appuser_gid)
        else:  # Windows系统
            # Windows不需要改变所有权，使用默认权限即可
            pass
        
        log_file_path = os.path.join(base_path, 'app.log')
        
        # 配置文件处理器
        file_handler = RotatingFileHandler(
            log_file_path, 
            maxBytes=10240000,
            backupCount=10,
            encoding='utf-8'
        )
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # 添加处理器到应用
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('应用启动')
        
    except PermissionError as e:
        print(f"{e}")
        #  fallback 到标准输出
        app.logger.warning("无法写入日志文件，使用控制台输出")
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
