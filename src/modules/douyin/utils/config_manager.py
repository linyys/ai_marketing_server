import os
from pathlib import Path
import yaml
import logging
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_user_config_base_path() -> Path:
    """获取用户配置基础路径"""
    app_data = os.getenv('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
    return Path(app_data) / 'ai_marketing_server'

def get_user_config_path(user_id: str, config_name: str = 'douyin_cookie.yaml') -> str:
    """获取用户配置文件路径"""
    # 构建用户配置目录路径
    user_dir = os.path.join(str(get_user_config_base_path()), 'users', str(user_id))
    
    # 确保用户配置目录存在
    if not os.path.exists(user_dir):
        try:
            os.makedirs(user_dir, exist_ok=True)
            logger.info(f"创建用户配置目录: {user_dir}")
        except Exception as e:
            logger.error(f"创建用户配置目录失败: {str(e)}")
            # 返回路径，但不保证目录存在
    
    # 返回配置文件完整路径
    return os.path.join(user_dir, config_name)

def ensure_user_config_directory(user_id: str) -> Path:
    """确保用户配置目录存在并返回路径"""
    user_dir = get_user_config_base_path() / 'users' / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

def backup_user_config(user_id: str, platform: str = 'douyin') -> Optional[Path]:
    """备份用户配置"""
    config_path = get_user_config_path(user_id, platform)
    if not config_path.exists():
        return None
    
    backup_path = config_path.with_suffix(f'.yaml.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    try:
        shutil.copy2(config_path, backup_path)
        logger.info(f"已备份用户{user_id}的{platform}配置到{backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"备份用户{user_id}的{platform}配置失败: {str(e)}")
        return None

def restore_user_config(user_id: str, backup_path: Path, platform: str = 'douyin') -> bool:
    """从备份恢复用户配置"""
    target_path = get_user_config_path(user_id, platform)
    try:
        shutil.copy2(backup_path, target_path)
        logger.info(f"已从{backup_path}恢复用户{user_id}的{platform}配置")
        return True
    except Exception as e:
        logger.error(f"恢复用户{user_id}的{platform}配置失败: {str(e)}")
        return False

def list_user_backups(user_id: str, platform: str = 'douyin') -> list:
    """列出用户配置的所有备份"""
    config_dir = get_user_config_base_path() / 'users' / user_id
    if not config_dir.exists():
        return []
    
    pattern = f'{platform}_config.yaml.bak.*'
    backups = []
    for file in config_dir.glob(pattern):
        try:
            # 解析备份时间戳
            timestamp_str = file.name.split('.')[-1]
            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
            backups.append({
                'path': str(file),
                'timestamp': timestamp,
                'formatted_time': timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception:
            # 忽略无效格式的备份文件
            continue
    
    # 按时间戳降序排序
    backups.sort(key=lambda x: x['timestamp'], reverse=True)
    return backups

def validate_config_structure(config: Dict[str, Any], required_sections: list) -> bool:
    """验证配置结构是否包含所有必要的部分"""
    for section in required_sections:
        if section not in config:
            logger.warning(f"配置缺少必要部分: {section}")
            return False
    return True

def clean_old_backups(user_id: str, platform: str = 'douyin', keep_days: int = 7) -> int:
    """清理指定天数前的备份文件"""
    config_dir = get_user_config_base_path() / 'users' / user_id
    if not config_dir.exists():
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    pattern = f'{platform}_config.yaml.bak.*'
    deleted_count = 0
    
    for file in config_dir.glob(pattern):
        try:
            # 解析备份时间戳
            timestamp_str = file.name.split('.')[-1]
            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
            
            if timestamp < cutoff_date:
                file.unlink()
                deleted_count += 1
                logger.info(f"已清理过期备份: {file}")
        except Exception:
            # 忽略无法解析时间戳的文件
            continue
    
    return deleted_count