# routes/__init__.py
"""
路由包初始化文件
将所有蓝图集中导出，方便管理
"""

from .spellingbee_routes import spellingbee_bp
from .auth_routes import auth_bp
# 导出所有蓝图
__all__ = ['spellingbee_bp','auth_bp']