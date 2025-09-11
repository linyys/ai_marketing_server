from fastapi import Request
import httpx
from utils import config, http_request
from utils.workflow_config import get_workflow_id_by_function
from typing import TypedDict


_token = config.config.get("coze", "token")
_base_url = "https://api.coze.cn/v1/workflow/stream_run"
_header = {
    "Authorization": "Bearer {}".format(_token),
    "Content-Type": "application/json",
}
_post = http_request.create_post(_base_url, _header)


async def forward_sse(request: Request, workflow_id: str, params: dict):
    body = {"workflow_id": workflow_id, "parameters": params}
    try:
        # 设置无限超时，防止长时间运行的流被中断
        async with httpx.AsyncClient(timeout=None) as client:
            print(f"开始流式请求: workflow_id={workflow_id}")
            async with client.stream(
                "POST", _base_url, headers=_header, json=body, timeout=None
            ) as upstream_response:
                # 检查上游响应状态
                if upstream_response.status_code != 200:
                    error_msg = f"data: Error: Upstream returned {upstream_response.status_code}\n\n"
                    print(f"流式请求错误: {error_msg}")
                    yield error_msg.encode()
                    return

                print(f"流式请求已连接，开始传输数据")
                # 转发每个事件块
                async for chunk in upstream_response.aiter_bytes():
                    if await request.is_disconnected():
                        print("客户端已断开连接")
                        break
                    yield chunk
                
                print("流式数据传输完成")

    except httpx.ReadTimeout as e:
        error_msg = f"data: Read timeout: {str(e)}\n\n"
        print(f"流式请求超时: {error_msg}")
        yield error_msg.encode()
    except httpx.ConnectTimeout as e:
        error_msg = f"data: Connection timeout: {str(e)}\n\n"
        print(f"流式请求连接超时: {error_msg}")
        yield error_msg.encode()
    except Exception as e:
        # 处理连接错误
        error_msg = f"data: Connection failed: {str(e)}\n\n"
        print(f"流式请求异常: {error_msg}")
        yield error_msg.encode()

class _test(TypedDict):
    input: str
async def test(request: Request, params: _test):
    return forward_sse(request, get_workflow_id_by_function("test"), params)



