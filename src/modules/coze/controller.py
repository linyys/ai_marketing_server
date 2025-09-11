from pydantic_core.core_schema import dataclass_field
from utils import config, http_request
from .task_manager import global_task_manager
from utils.workflow_config import get_workflow_id_by_function
from typing import TypedDict, List, Dict, Any
from fastapi import UploadFile, HTTPException
import httpx

_token = config.config.get("coze", "token")


# 成功返回的数据格式
class WorkflowResponse(TypedDict):
    task_id: str
    message: str

_file_base_url = "https://api.coze.cn/v1/files/upload"
_file_header = {
    "Authorization": "Bearer {}".format(_token),
}
async def file_to_fileid(file: UploadFile) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(_file_base_url, headers=_file_header, files={"file": file.file})
            response.raise_for_status()
            data = response.json()
            return data["data"]["id"]
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"文件上传失败：{e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败：{str(e)}")


_base_url = "https://api.coze.cn/v1/workflow/run"
_header = {
    "Authorization": "Bearer {}".format(_token),
    "Content-Type": "application/json",
}
_post = http_request.create_post(_base_url, _header)
async def base_workflow(workflow_id: str, params: dict) -> WorkflowResponse:
    body = {"workflow_id": workflow_id, "parameters": params, "is_async": True}
    res = await _post("", json=body)
    if res["code"] == 0:
        task_id = res["execute_id"]
        print(task_id)
        global_task_manager.add_task(
            task_id=task_id, workflow_id=body["workflow_id"]
        )
        return {"task_id": task_id, "message": "工作流已启动"}
    else:
        raise HTTPException(status_code=500, detail=f"工作流执行失败：{res['msg']}")
