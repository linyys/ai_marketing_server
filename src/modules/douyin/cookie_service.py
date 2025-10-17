import logging
import yaml
import os
import threading
from pathlib import Path
from typing import List, Callable, Any, Dict
from datetime import datetime
import re
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

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

# 全局Cookie管理器实例
CONFIG_PATH = "src/modules/douyin/web/config.yaml"
cookie_manager = CookieManager(CONFIG_PATH)