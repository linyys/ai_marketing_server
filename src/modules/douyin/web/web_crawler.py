import asyncio
import logging
import os
import threading
from urllib.parse import urlencode, quote
from .abogus import ABogus
from .utils import (AwemeIdFetcher, generate_base_params, generate_webid, generate_uifid)
import yaml
from pathlib import Path
from src.modules.douyin.utils.config_manager import get_user_config_path as get_user_cookie_path

from src.modules.douyin.base_crawler import BaseCrawler
from src.modules.douyin.web.endpoints import DouyinAPIEndpoints
from src.modules.douyin.web.models import (
    PostComments, PostDetail, UserProfile, UserPost
)
from src.modules.douyin.web.utils import BogusManager

# 初始化logger实例
logger = logging.getLogger(__name__)

class DouyinWebCrawler:
    def __init__(self, user_id: str = None):
        """
        初始化抖音Web爬虫
        
        Args:
            user_id: 可选的用户ID，用于加载用户专属配置
        """
        self.user_id = user_id
        self._config_lock = threading.RLock()
        self.abogus = BogusManager()  # 初始化abogus
        
        # 集成 cookie_manager
        from src.modules.douyin.cookie_service import cookie_manager as global_cookie_manager
        self.cookie_manager = global_cookie_manager
        self.user_mode_enabled = self.cookie_manager.is_user_specific_mode()
        
        # 选择配置路径
        if user_id:
            # 用户专属模式
            self.config_path = get_user_cookie_path(user_id)
        else:
            # 全局模式（保持向后兼容）
            self.config_path = Path("src/modules/douyin/web/config.yaml")
        
        self._load_config()
    
    def _load_config(self):
        """安全加载配置（线程安全）"""
        with self._config_lock:
            try:
                if self.config_path.exists():
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        self.headers = config['TokenManager']['douyin']['headers']
                        self.cookies = self._parse_cookies(self.headers.get('Cookie', ''))
                        # 加载额外的用户配置项
                        self.timeout = config.get('timeout', 30)
                        self.retry_count = config.get('retry_count', 3)
                        self.proxy = config.get('proxy', None)
                    logger.debug(f"{'用户' + self.user_id if self.user_id else '全局'}：成功加载配置")
                else:
                    # 使用默认配置
                    self.headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
                    }
                    self.cookies = {}
                    self.timeout = 30
                    self.retry_count = 3
                    self.proxy = None
                    logger.warning(f"{'用户' + self.user_id if self.user_id else '全局'}：配置文件不存在，使用默认配置")
            except Exception as e:
                logger.error(f"{'用户' + self.user_id if self.user_id else '全局'}：加载配置失败: {str(e)}")
                # 加载失败时使用安全默认值
                self.headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
                }
                self.cookies = {}
                self.timeout = 30
                self.retry_count = 3
                self.proxy = None
                # 尝试从全局配置回退
                if self.user_id:
                    try:
                        global_config_path = Path("src/modules/douyin/web/config.yaml")
                        if global_config_path.exists():
                            with open(global_config_path, 'r', encoding='utf-8') as f:
                                config = yaml.safe_load(f)
                                self.headers = config['TokenManager']['douyin']['headers']
                                self.cookies = self._parse_cookies(self.headers.get('Cookie', ''))
                            logger.info(f"用户{self.user_id}配置加载失败，已回退到全局配置")
                    except:
                        pass
    
    def reload_config(self):
        """外部调用的配置重载方法"""
        self._load_config()
        logger.info("抖音爬虫配置已重新加载")
    
    def cleanup(self):
        """清理资源（用于实例替换）"""
        pass
        
    def _parse_cookies(self, cookie_str: str) -> dict:
        """安全解析Cookie字符串，避免IndexError"""
        cookies = {}
        if not cookie_str:
            return cookies
        for cookie in cookie_str.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)  # 只分割一次，避免多等号问题
                cookies[key] = value
        return cookies

    async def get_douyin_headers(self):
        """获取抖音请求头配置"""
        with self._config_lock:
            douyin_config = {
                "headers": self.headers.copy(),
                "proxies": {
                    "http": self.headers.get("http", ""),
                    "https": self.headers.get("https", "")
                }
            }
            kwargs = {
                "headers": {
                    "Accept-Language": douyin_config["headers"]["Accept-Language"],
                    "User-Agent": douyin_config["headers"]["User-Agent"],
                    "Referer": douyin_config["headers"]["Referer"],
                    "Cookie": douyin_config["headers"]["Cookie"],
                },
                "proxies": {"http": douyin_config["proxies"]["http"], "https": douyin_config["proxies"]["https"]},
            }
        return kwargs

    async def fetch_one_video(self, aweme_id: str):
        """获取单个作品数据"""
        kwargs = await self.get_douyin_headers()
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            params = PostDetail(aweme_id=aweme_id)
            params_dict = params.dict()
            params_dict["msToken"] = ''
            a_bogus = BogusManager.ab_model_2_endpoint(params_dict, kwargs["headers"]["User-Agent"])
            endpoint = f"{DouyinAPIEndpoints.POST_DETAIL}?{urlencode(params_dict)}&a_bogus={a_bogus}"
            response = await crawler.fetch_get_json(endpoint)
        return response

    async def fetch_user_post_videos(self, sec_user_id: str, max_cursor: int, count: int):
        """获取用户发布作品数据"""
        kwargs = await self.get_douyin_headers()
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            params = UserPost(sec_user_id=sec_user_id, max_cursor=max_cursor, count=count)
            params_dict = params.dict()
            params_dict["msToken"] = ''
            a_bogus = BogusManager.ab_model_2_endpoint(params_dict, kwargs["headers"]["User-Agent"])
            endpoint = f"{DouyinAPIEndpoints.USER_POST}?{urlencode(params_dict)}&a_bogus={a_bogus}"
            response = await crawler.fetch_get_json(endpoint)
        return response

    async def handler_user_profile(self, sec_user_id: str):
        """获取指定用户的信息"""
        kwargs = await self.get_douyin_headers()
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            params = UserProfile(sec_user_id=sec_user_id)
            endpoint = BogusManager.xb_model_2_endpoint(
                DouyinAPIEndpoints.USER_DETAIL, params.dict(), kwargs["headers"]["User-Agent"]
            )
            response = await crawler.fetch_get_json(endpoint)
        return response

    async def fetch_video_comments(self, aweme_id: str, cursor: int = 0, count: int = 20):
        """获取指定视频的评论数据"""
        kwargs = await self.get_douyin_headers()
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            params = PostComments(aweme_id=aweme_id, cursor=cursor, count=count)
            endpoint = BogusManager.xb_model_2_endpoint(
                DouyinAPIEndpoints.POST_COMMENT, params.dict(), kwargs["headers"]["User-Agent"]
            )
            response = await crawler.fetch_get_json(endpoint)
        return response

    # 获取搜索关键词建议
    async def get_search_suggestions(self, keyword: str):
        """
        获取抖音搜索关键词的推荐建议
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            推荐词列表，格式: [{"content": "推荐词1", ...}, ...]
        """
        # 获取抖音的实时Cookie和请求头
        kwargs = await self.get_douyin_headers()
        
        # 基础参数（复用现有生成方法）
        params = generate_base_params()
        params.update({
            "keyword": keyword,
            "source": "aweme_video_web",
            "update_version_code": "170400",
            "pc_client_type": "1",
            "pc_libra_divert": "Windows",
            "webid": generate_webid(),
            "uifid": generate_uifid(),
        })
        
        # 动态生成关键参数
        params["a_bogus"] = BogusManager.ab_model_2_endpoint(params, kwargs["headers"]["User-Agent"])
        params["msToken"] = self._generate_ms_token()  # 可复用xbogus.py的逻辑
        
        # 发送请求
        url = "https://www.douyin.com/aweme/v1/web/search/sug/?"
        async with BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"]) as crawler:
            endpoint = f"{url}{urlencode(params)}"
            response = await crawler.fetch_get_json(endpoint)
        
        # 解析响应
        return response.get("sug_list", [])

    async def search_videos(self, keyword: str, offset: int = 0, count: int = 16) -> dict:
        """
        搜索关键词相关视频，返回搜索结果（参数严格匹配实际请求）
        
        Args:
            keyword: 搜索关键词
            offset: 分页偏移量
            count: 每页数量
            
        Returns:
            搜索结果字典，包含视频列表等信息
        """
        # 获取抖音的实时Cookie和请求头
        kwargs = await self.get_douyin_headers()
        
        # 构建搜索参数（完全匹配实际参数）
        params = generate_base_params()
        params.update({
            "keyword": keyword,
            "search_channel": "aweme_video_web",
            "list_type": "single",
            "search_source": "normal_search",
            "offset": str(offset),
            "count": str(count),
            "webid": generate_webid(),
            "uifid": generate_uifid(),
        })
        
        # 生成a_bogus参数
        params["a_bogus"] = BogusManager.ab_model_2_endpoint(params, kwargs["headers"]["User-Agent"])
        params["msToken"] = self._generate_ms_token()
        
        # 发送请求
        url = DouyinAPIEndpoints.SEARCH_ITEM
        async with BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"]) as crawler:
            endpoint = f"{url}?{urlencode(params)}"
            response = await crawler.fetch_get_json(endpoint)
        
        return response

    def _get_search_headers(self, keyword: str) -> dict:
        """生成搜索请求专用headers"""
        referer = f"https://www.douyin.com/search/{quote(keyword)}?type=video"
        return {
            **self.headers,
            "referer": referer,
            "priority": "u=1, i",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }

    def _generate_ms_token(self) -> str:
        """生成msToken"""
        from src.modules.douyin.web.utils import TokenManager
        return TokenManager().gen_real_msToken()

    def get_cookie(self, user_id: str = None) -> dict:
        """获取Cookie配置"""
        # 保持使用 _load_config 加载的配置，与类的其他部分保持一致
        with self._config_lock:
            return self.cookies.copy()  # 返回当前加载的Cookie副本
        