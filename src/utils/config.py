import configparser
import os
from typing import Optional


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
config = configparser.ConfigParser()

# 尝试多个可能的配置文件路径
config_paths = [
    os.path.join(BASE_DIR, "..", "config.ini"),  # Docker环境中的路径
    os.path.join(BASE_DIR, "..", "..", "config.ini"),  # 本地环境中的路径
    "config.ini"  # 当前工作目录
]

config_loaded = False
for config_path in config_paths:
    if os.path.exists(config_path):
        config.read(config_path)
        print(f"配置文件已加载: {config_path}")
        config_loaded = True
        break

if not config_loaded:
    print("未找到config.ini文件，将使用环境变量或默认值")


def get_redis_config() -> dict:
    """获取Redis配置，优先从环境变量获取"""
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_db = os.getenv('REDIS_DB', '0')
    redis_password = os.getenv('REDIS_PASSWORD')
    
    # 如果环境变量不存在，从配置文件获取
    if not redis_host or not redis_port:
        if config.has_section('redis'):
            redis_host = redis_host or config.get('redis', 'host', fallback='192.168.0.44')
            redis_port = redis_port or config.get('redis', 'port', fallback='6379')
            redis_db = redis_db or config.get('redis', 'db', fallback='0')
            redis_password = redis_password or config.get('redis', 'password', fallback=None)
        else:
            # 使用默认值
            redis_host = redis_host or '192.168.0.44'
            redis_port = redis_port or '6379'
    
    return {
        'host': redis_host,
        'port': redis_port,
        'db': redis_db,
        'password': redis_password
    }


def get_mysql_config() -> dict:
    """获取MySQL配置，优先从环境变量获取"""
    mysql_host = os.getenv('MYSQL_HOST')
    mysql_port = os.getenv('MYSQL_PORT')
    mysql_database = os.getenv('MYSQL_DATABASE')
    mysql_user = os.getenv('MYSQL_USER')
    mysql_password = os.getenv('MYSQL_PASSWORD')
    
    # 如果环境变量不存在，从配置文件获取
    if not all([mysql_host, mysql_port, mysql_database, mysql_user, mysql_password]):
        if config.has_section('mysql'):
            mysql_host = mysql_host or config.get('mysql', 'host', fallback='localhost')
            mysql_port = mysql_port or config.get('mysql', 'port', fallback='3306')
            mysql_database = mysql_database or config.get('mysql', 'database', fallback='class_bot_server')
            mysql_user = mysql_user or config.get('mysql', 'user', fallback='root')
            mysql_password = mysql_password or config.get('mysql', 'password', fallback='root123')
        else:
            # 使用默认值
            mysql_host = mysql_host or 'localhost'
            mysql_port = mysql_port or '3306'
            mysql_database = mysql_database or 'class_bot_server'
            mysql_user = mysql_user or 'app_user'
            mysql_password = mysql_password or 'app_password'
    
    return {
        'host': mysql_host,
        'port': mysql_port,
        'database': mysql_database,
        'user': mysql_user,
        'password': mysql_password
    }


def get_redis_url() -> str:
    """获取Redis连接URL"""
    redis_config = get_redis_config()
    if redis_config['password']:
        return f"redis://:{redis_config['password']}@{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"
    else:
        return f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"


def get_database_url() -> str:
    """获取数据库连接URL"""
    mysql_config = get_mysql_config()
    return f"mysql+pymysql://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}?charset=utf8mb4"


def get_state_config() -> dict:
    """获取状态配置"""
    return {
        'SUCCESS': config.get('state', 'SUCCESS', fallback='0'),
        'FAILED': config.get('state', 'FAILED', fallback='1')
    }


def get_coze_config() -> dict:
    """获取Coze配置"""
    return {
        'token': config.get('coze', 'token', fallback='')
    }


def get_ppt_config() -> dict:
    """获取PPT配置"""
    return {
        'api_key': config.get('ppt', 'api_key', fallback='')
    }


def get_human_config() -> dict:
    """获取数字人配置"""
    return {
        'max_concurrent': int(config.get('human', 'max_concurrent', fallback='1')),
        'gradio_url': config.get('human', 'gradio_url', fallback='http://192.168.0.44:7860/')
    }


def get_tts_config() -> dict:
    """获取TTS配置"""
    return {
        'max_concurrent': int(config.get('tts', 'max_concurrent', fallback='1')),
        'gradio_url': config.get('tts', 'gradio_url', fallback='http://192.168.0.44:7866/')
    }