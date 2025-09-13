from utils import config, http_request
from modules.coze.task_manager import global_task_manager
SUCCESS = config.config.get("state", "SUCCESS")
FAILED = config.config.get("state", "FAILED")
_token = config.config.get('coze', 'token')
_base_url = "https://api.coze.cn/v1"
_header = {"Authorization": "Bearer {}".format(_token), "Content-Type": "application/json"}
_get = http_request.create_get(_base_url, _header)


async def query_workflow(task_id, workflow_id):
  url = "/workflows/{}/run_histories/{}".format(workflow_id, task_id)
  # print(url)
  res = await _get(url)
  if (res["code"] == 4200):
    return { "code": FAILED, "msg": "失败" }
  print(res)
  history = res["data"][0]
  if (history["execute_status"] == "Success"):
    global_task_manager.delete_task(task_id)
    return { "data": history["output"], "code": SUCCESS, "msg": "成功" }
  elif (history["execute_status"] == "Fail"):
    return { "code": FAILED, "msg": "失败" }
  else:
    return {  "code": SUCCESS, "msg": "未执行完毕" }