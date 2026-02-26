import os
from datetime import timedelta
class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    HOST=os.getenv('PGHOST','127.0.0.1')
    PORT=os.getenv('PGPORT','5432')
    DBNAME=os.getenv('PGDATABASE','franchdb')
    USER=os.getenv('PGUSER','franchuser')
    PASSWORD=os.getenv('PGPASSWORD','franchpass')
    
    # Docker环境配置
    if os.environ.get('DOCKER_ENV'):
        pass

class ProductionConfig(BaseConfig):
    """生产环境配置"""
    pass

class TestingConfig(BaseConfig):
    """测试环境配置"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'hard-to-guess-string'

# 默认配置
Config = BaseConfig