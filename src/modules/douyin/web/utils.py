import json
import logging
import random
import string
import time
import re
from urllib.parse import quote

import httpx
import yaml

from modules.douyin.utils.api_exceptions import (
    APIConnectionError,
    APIResponseError,
    APINotFoundError,
    APIUnauthorizedError,
)
from modules.douyin.utils.utils import get_timestamp, gen_random_str
from modules.douyin.web.xbogus import XBogus
from modules.douyin.web.abogus import ABogus

logger = logging.getLogger(__name__)

# 读取配置文件
with open("src/modules/douyin/web/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class TokenManager:
    douyin_manager = config.get("TokenManager").get("douyin")
    token_conf = douyin_manager.get("msToken")
    ttwid_conf = douyin_manager.get("ttwid")
    proxies = douyin_manager.get("proxies")

    @classmethod
    def gen_real_msToken(cls) -> str:
        """
        生成真实的msToken (Generate real msToken)
        """
        payload = json.dumps(
            {
                "magic": cls.token_conf["magic"],
                "version": cls.token_conf["version"],
                "dataType": cls.token_conf["dataType"],
                "strData": cls.token_conf["strData"],
                "tspFromClient": get_timestamp(),
            }
        )
        headers = {
            "User-Agent": cls.token_conf["User-Agent"],
            "Content-Type": "application/json",
        }

        transport = httpx.HTTPTransport(retries=5)
        with httpx.Client(transport=transport) as client:
            try:
                response = client.post(
                    cls.token_conf["url"], content=payload, headers=headers
                )
                response.raise_for_status()

                msToken = str(httpx.Cookies(response.cookies).get("msToken"))
                if len(msToken) not in [120, 128]:
                    raise APIResponseError("响应内容：{0}， Douyin msToken API 的响应内容不符合要求。".format(msToken))

                return msToken

            except Exception as e:
                # 返回虚假的msToken (Return a fake msToken)
                logger.error("请求Douyin msToken API时发生错误：{0}".format(e))
                logger.info("将使用本地生成的虚假msToken参数，以继续请求。")
                return cls.gen_false_msToken()

    @classmethod
    def gen_false_msToken(cls) -> str:
        """生成随机msToken (Generate random msToken)"""
        return gen_random_str(126) + "=="


class BogusManager:

    # 字典方法生成X-Bogus参数
    @classmethod
    def xb_model_2_endpoint(cls, base_endpoint: str, params: dict, user_agent: str) -> str:
        if not isinstance(params, dict):
            raise TypeError("参数必须是字典类型")

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])

        try:
            xb_value = XBogus(user_agent).getXBogus(param_str)
        except Exception as e:
            raise RuntimeError("生成X-Bogus失败: {0})".format(e))

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}&X-Bogus={xb_value[1]}"

        return final_endpoint

    # 字典方法生成A-Bogus参数
    @classmethod
    def ab_model_2_endpoint(cls, params: dict, user_agent: str) -> str:
        if not isinstance(params, dict):
            raise TypeError("参数必须是字典类型")

        try:
            ab_value = ABogus().get_value(params, )
        except Exception as e:
            raise RuntimeError("生成A-Bogus失败: {0})".format(e))

        return quote(ab_value, safe='')


class AwemeIdFetcher:
    # 预编译正则表达式
    _DOUYIN_VIDEO_URL_PATTERN = re.compile(r"video/([^/?]*)")
    _DOUYIN_VIDEO_URL_PATTERN_NEW = re.compile(r"[?&]vid=(\\d+)")
    _DOUYIN_NOTE_URL_PATTERN = re.compile(r"note/([^/?]*)")
    _DOUYIN_DISCOVER_URL_PATTERN = re.compile(r"modal_id=([0-9]+)")

    @classmethod
    async def get_aweme_id(cls, url: str) -> str:
        """
        从单个url中获取aweme_id (Get aweme_id from a single url)

        Args:
            url (str): 输入的url (Input url)

        Returns:
            str: 匹配到的aweme_id (Matched aweme_id)
        """

        if not isinstance(url, str):
            raise TypeError("参数必须是字符串类型")

        # 重定向到完整链接
        transport = httpx.AsyncHTTPTransport(retries=5)
        async with httpx.AsyncClient(
                transport=transport, proxy=None, timeout=10
        ) as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                response_url = str(response.url)

                # 按顺序尝试匹配视频ID
                for pattern in [
                    cls._DOUYIN_VIDEO_URL_PATTERN,
                    cls._DOUYIN_VIDEO_URL_PATTERN_NEW,
                    cls._DOUYIN_NOTE_URL_PATTERN,
                    cls._DOUYIN_DISCOVER_URL_PATTERN
                ]:
                    match = pattern.search(response_url)
                    if match:
                        return match.group(1)

                raise APIResponseError("未在响应的地址中找到 aweme_id，检查链接是否为作品页")

            except httpx.RequestError as exc:
                raise APIConnectionError(
                    f"请求端点失败，请检查当前网络环境。链接：{url}，代理：{TokenManager.proxies}，异常类名：{cls.__name__}，异常详细信息：{exc}"
                )

            except httpx.HTTPStatusError as e:
                raise APIResponseError(
                    f"链接：{e.response.url}，状态码 {e.response.status_code}：{e.response.text}"
                )


def generate_base_params() -> dict:
    """生成抖音搜索基础参数"""
    return {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "support_h265": "0",
        "support_dash": "0",
        "cpu_core_num": "12",
        "version_code": "170400",
        "version_name": "17.4.0",
        "cookie_enabled": "true",
        "screen_width": "1536",
        "screen_height": "864",
        "browser_language": "zh-CN",
        "browser_platform": "Win32",
        "browser_name": "Edge",
        "browser_version": "141.0.0.0",
        "browser_online": "true",
        "engine_name": "Blink",
        "engine_version": "141.0.0.0",
        "os_name": "Windows",
        "os_version": "10",
        "device_memory": "8",
        "platform": "PC",
        "downlink": "10",
        "effective_type": "4g",
        "round_trip_time": "50",
    }


def generate_webid() -> str:
    """生成webid参数"""
    import random
    return str(random.randint(1000000000000000000, 9999999999999999999))


def generate_uifid() -> str:
    """生成uifid参数"""
    import uuid
    return uuid.uuid4().hex
