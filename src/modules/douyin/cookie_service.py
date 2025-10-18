import logging
import yaml
import os
import threading
from pathlib import Path
from typing import List, Callable, Any, Dict
from datetime import datetime
import re
from fastapi import HTTPException, status
from datetime import timedelta
from src.modules.douyin.utils.config_manager import get_user_config_path as get_user_cookie_path

logger = logging.getLogger(__name__)

def get_user_cookie_path(user_id: str) -> Path:
    """获取用户专属Cookie配置文件路径"""
    app_data = os.getenv('APPDATA', os.path.expanduser('~\AppData\Roaming'))
    return Path(app_data) / 'ai_marketing_server' / 'users' / user_id / 'douyin_cookie.yaml'

class UserCookieManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.cookie_path = get_user_cookie_path(user_id)
        self._ensure_directory()
    
    def _ensure_directory(self):
        """确保用户目录存在"""
        self.cookie_path.parent.mkdir(parents=True, exist_ok=True)
    
    def is_valid(self) -> bool:
        """检查用户配置是否存在且有效"""
        return self.cookie_path.exists()
    
    def update_user_cookie(self, cookie_str: str) -> Dict[str, str]:
        """用户专属Cookie更新（不替换现有方法）"""
        # 验证必要字段
        required_fields = ['sessionid', 'sid_guard', 'uid_tt', 'd_ticket']
        if not all(field in cookie_str for field in required_fields):
            return {"status": "error", "detail": "Cookie不完整"}
        
        # 保存到用户专属文件
        config = {
            'TokenManager': {
                'douyin': {
                    'headers': {
                        'Cookie': cookie_str.strip(),
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
                    }
                }
            },
            'last_updated': datetime.utcnow().isoformat()  # 添加更新时间戳
        }
        
        # 备份现有配置
        if self.cookie_path.exists():
            backup_path = self.cookie_path.with_suffix('.yaml.bak')
            try:
                import shutil
                shutil.copy2(self.cookie_path, backup_path)
                logger.info(f"已备份用户{self.user_id}的Cookie配置")
            except Exception as e:
                logger.warning(f"备份Cookie配置失败: {str(e)}")
        
        # 自动创建配置文件
        with open(self.cookie_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, allow_unicode=True)
        
        return {"status": "success", "user_id": self.user_id}
    
    # 添加新方法：恢复配置
    def restore_from_backup(self) -> Dict[str, str]:
        """从备份恢复用户Cookie配置"""
        backup_path = self.cookie_path.with_suffix('.yaml.bak')
        if not backup_path.exists():
            return {"status": "error", "detail": "备份文件不存在"}
        
        try:
            import shutil
            shutil.copy2(backup_path, self.cookie_path)
            logger.info(f"已从备份恢复用户{self.user_id}的Cookie配置")
            return {"status": "success", "user_id": self.user_id}
        except Exception as e:
            logger.error(f"恢复Cookie配置失败: {str(e)}")
            return {"status": "error", "detail": str(e)}
    
    def get_cookie(self, user_id: str) -> dict:
        """获取指定用户的Cookie配置"""
        try:
            # 先尝试获取用户专属配置
            cookie_config = self._load_user_cookie(user_id)
            if cookie_config:
                return cookie_config
            
            # 如果用户专属配置不存在，创建一个基于全局配置的用户专属配置
            logger.info(f"用户 {user_id} 的专属配置不存在，自动创建")
            global_config = self._load_global_cookie()
            self._save_user_cookie(user_id, global_config)
            return global_config
        except Exception as e:
            logger.error(f"获取用户Cookie配置失败: {str(e)}")
            # 出错时返回全局配置
            return self._load_global_cookie()

class CookieManager:
    """管理抖音Cookie的更新与验证"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self._validate_config_path()
        
    def _validate_config_path(self):
        """验证配置文件路径有效性"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        if not os.access(self.config_path, os.W_OK):
            raise PermissionError(f"无权写入配置文件: {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """安全加载YAML配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="配置文件加载失败"
            )
    
    def _save_config(self, config: Dict[str, Any]):
        """安全保存YAML配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="配置文件保存失败"
            )
    
    def _validate_douyin_cookie(self, cookie_str: str) -> bool:
        """验证抖音Cookie是否包含必要字段"""
        required_fields = [
            'sessionid', 'sid_guard', 'uid_tt', 'd_ticket',
            's_v_web_id', 'xgplayer_user_id'
        ]
        
        # 检查所有必要字段是否存在
        for field in required_fields:
            if f"{field}=" not in cookie_str:
                logger.warning(f"Cookie验证失败: 缺少必要字段 {field}")
                return False
        
        return True
    
    # 添加回调存储和锁机制
    _update_callbacks: List[Callable[[], None]] = []
    _callback_lock = threading.RLock()
    
    @classmethod
    def register_update_callback(cls, callback: Callable[[], None]):
        """
        注册配置更新回调函数
        """
        with cls._callback_lock:
            if callback not in cls._update_callbacks:
                cls._update_callbacks.append(callback)
    
    def update_cookie(self, cookie_str: str) -> Dict[str, str]:
        """
        更新抖音Cookie
        
        Args:
            cookie_str: 完整的Cookie字符串
            
        Returns:
            Dict[str, str]: 操作结果
        """
        # 验证Cookie完整性
        if not self._validate_douyin_cookie(cookie_str):
            logger.warning("拒绝更新: Cookie不完整")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cookie不完整，缺少必要字段"
            )
        
        # 保存配置
        config = self._load_config()
        config['TokenManager']['douyin']['headers']['Cookie'] = cookie_str.strip()
        self._save_config(config)
        
        # 触发所有注册的回调（错误隔离处理）
        with self._callback_lock:
            for callback in self._update_callbacks[:]:
                try:
                    callback()
                    logger.debug("成功执行Cookie更新回调")
                except Exception as e:
                    logger.error(f"Cookie更新回调执行失败: {str(e)}")
        
        logger.info("成功更新抖音Cookie并通知所有监听器")
        return {
            "status": "success",
            "message": "Cookie更新成功",
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def is_user_specific_mode(self) -> bool:
        """判断是否启用用户专属模式"""
        # 从配置中读取用户专属模式状态
        try:
            config = self._load_config()
            return config.get('user_specific_mode', False)
        except:
            return False  # 默认禁用，保持向后兼容
    
    # 添加新方法：切换用户专属模式
    def toggle_user_specific_mode(self, enable: bool) -> Dict[str, str]:
        """切换用户专属模式"""
        try:
            config = self._load_config()
            config['user_specific_mode'] = enable
            self._save_config(config)
            logger.info(f"用户专属模式已{'启用' if enable else '禁用'}")
            return {"status": "success", "mode": "user_specific" if enable else "global"}
        except Exception as e:
            logger.error(f"切换用户专属模式失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="切换模式失败"
            )
    
    # 添加新方法：清理过期的用户配置
    def cleanup_expired_user_configs(self, days: int = 30) -> Dict[str, str]:
        """清理指定天数未更新的用户配置"""
        try:
            app_data = os.getenv('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
            users_dir = Path(app_data) / 'ai_marketing_server' / 'users'
            if not users_dir.exists():
                return {"status": "success", "cleaned_count": 0}
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            cleaned_count = 0
            
            for user_dir in users_dir.iterdir():
                if user_dir.is_dir():
                    cookie_file = user_dir / 'douyin_cookie.yaml'
                    if cookie_file.exists():
                        try:
                            with open(cookie_file, 'r', encoding='utf-8') as f:
                                config = yaml.safe_load(f)
                                last_updated = config.get('last_updated')
                                if last_updated:
                                    last_updated_date = datetime.fromisoformat(last_updated)
                                    if last_updated_date < cutoff_date:
                                        cookie_file.unlink()
                                        backup_file = cookie_file.with_suffix('.yaml.bak')
                                        if backup_file.exists():
                                            backup_file.unlink()
                                        cleaned_count += 1
                                        logger.info(f"已清理用户{user_dir.name}的过期配置")
                        except Exception as e:
                            logger.warning(f"处理用户{user_dir.name}的配置时出错: {str(e)}")
            
            return {"status": "success", "cleaned_count": cleaned_count}
        except Exception as e:
            logger.error(f"清理过期配置失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="清理配置失败"
            )

# 全局Cookie管理器实例
CONFIG_PATH = "src/modules/douyin/web/config.yaml"
cookie_manager = CookieManager(CONFIG_PATH)