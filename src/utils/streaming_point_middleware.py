import json
from typing import AsyncGenerator, Optional
from sqlalchemy.orm import Session

from .point_service import PointService


async def wrap_sse_with_point_deduction(
    upstream_generator: AsyncGenerator[bytes, None],
    db: Session,
    user_uid: str,
    workflow_id: str,
    from_user_uid: Optional[str] = None,
) -> AsyncGenerator[bytes, None]:
    """
    包装上游 SSE 字节流：
    - 一边转发给下游客户端
    - 一边解析 "data:" 行的内容，聚合文本以进行按字符扣费
    - 流结束后进行扣费（allow_negative=True），避免中途断流
    """
    aggregated_text_parts: list[str] = []

    try:
        async for chunk in upstream_generator:
            # 转发原始字节
            try:
                decoded = chunk.decode("utf-8", errors="ignore")
            except Exception:
                decoded = ""

            # 简单解析 SSE 格式：仅处理以 "data:" 开头的行
            if decoded:
                for line in decoded.splitlines():
                    if line.startswith("data:"):
                        payload = line[len("data:") :].strip()
                        if not payload:
                            continue
                        # 尝试解析 JSON，如果是结构化数据，优先提取 content 字段
                        try:
                            obj = json.loads(payload)
                            if isinstance(obj, dict):
                                content = obj.get("content")
                                if isinstance(content, str):
                                    aggregated_text_parts.append(content)
                                else:
                                    # 如果没有 content 字段，则聚合原始文本化的 JSON
                                    aggregated_text_parts.append(payload)
                            else:
                                aggregated_text_parts.append(str(obj))
                        except Exception:
                            # 非 JSON，按纯文本聚合
                            aggregated_text_parts.append(payload)
            # 将块直接下发给客户端
            yield chunk
    finally:
        # 在流结束后进行扣费（允许负数，避免中途断流）
        aggregated_text = "".join(aggregated_text_parts)
        try:
            PointService.consume_points_by_response(
                db=db,
                user_uid=user_uid,
                from_user_uid=from_user_uid,
                workflow_id=workflow_id,
                response_text=aggregated_text,
                allow_negative=True,
                record_desc_prefix=f"流式扣费: workflow_id={workflow_id}",
            )
        except Exception:
            # 扣费失败不影响流式传输的完成（可在日志系统里记录）
            pass