import asyncio
import os
from urllib.parse import urlencode
from .abogus import ABogus
from .utils import (AwemeIdFetcher, generate_base_params, generate_webid, generate_uifid)
import yaml

from modules.douyin.base_crawler import BaseCrawler
from modules.douyin.web.endpoints import DouyinAPIEndpoints
from modules.douyin.web.models import (
    PostComments, PostDetail, UserProfile, UserPost
)
from modules.douyin.web.utils import BogusManager

# 配置文件路径
path = os.path.abspath(os.path.dirname(__file__))

# 读取配置文件
with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class DouyinWebCrawler:
    def __init__(self):
        self.headers = config["TokenManager"]["douyin"]["headers"]
        self.proxies = config["TokenManager"]["douyin"]["proxies"]
        self.session = BaseCrawler(proxies=self.proxies, crawler_headers=self.headers)
        self.abogus = ABogus()

    async def get_douyin_headers(self):
        """获取抖音请求头配置"""
        douyin_config = config["TokenManager"]["douyin"]
        kwargs = {
            "headers": {
                "Accept-Language": douyin_config["headers"]["Accept-Language"],
                "User-Agent": douyin_config["headers"]["User-Agent"],
                "Referer": douyin_config["headers"]["Referer"],
                "Cookie": douyin_config["headers"]["Cookie"],
            },
            "proxies": {"http://": douyin_config["proxies"]["http"], "https://": douyin_config["proxies"]["https"]},
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
        params["a_bogus"] = self.abogus.get_value(params)
        params["msToken"] = self._generate_ms_token()  # 可复用xbogus.py的逻辑
        
        # 发送请求
        url = "https://www.douyin.com/aweme/v1/web/search/sug/?" + urlencode(params)
        response = await self.session.fetch_get_json(url)
        
        # 解析响应
        return response.get("sug_list", [])

    def _generate_ms_token(self) -> str:
        """复用TokenManager的token生成逻辑"""
        from .utils import TokenManager
        return TokenManager().gen_real_msToken()
