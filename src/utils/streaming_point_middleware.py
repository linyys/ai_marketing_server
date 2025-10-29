import json
from typing import AsyncGenerator, Optional, Any
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
    # 仅统计字符总数，避免聚合大文本造成内存占用
    char_count: int = 0
    # 行缓冲，保证跨 chunk 的行不会被截断
    buffer: str = ""

    def _count_text_in_json(obj: Any) -> int:
        """粗略统计 JSON 中的文本长度：优先常见字段，其次遍历所有字符串值。"""
        try:
            if isinstance(obj, dict):
                # 优先常见字段
                for key in ("content", "text", "output", "result"):
                    v = obj.get(key)
                    if isinstance(v, str):
                        return len(v)
                # 次级：遍历所有字符串值（避免过度累加，仅取总长度）
                total = 0
                stack = [obj]
                while stack:
                    cur = stack.pop()
                    if isinstance(cur, dict):
                        for v in cur.values():
                            stack.append(v)
                    elif isinstance(cur, list):
                        for v in cur:
                            stack.append(v)
                    elif isinstance(cur, str):
                        total += len(cur)
                return total
            elif isinstance(obj, list):
                return sum(_count_text_in_json(x) for x in obj)
            elif isinstance(obj, str):
                return len(obj)
            else:
                return len(str(obj))
        except Exception:
            return 0

    try:
        async for chunk in upstream_generator:
            # 转发原始字节
            try:
                decoded = chunk.decode("utf-8", errors="ignore")
            except Exception:
                decoded = ""

            # 累积到缓冲，保证跨 chunk 的行不丢失
            if decoded:
                buffer += decoded

                # 逐行处理，仅在完整行时计数（保留最后未结束的部分）
                while True:
                    idx = buffer.find("\n")
                    if idx == -1:
                        break
                    line = buffer[:idx]
                    buffer = buffer[idx + 1 :]

                    if line.startswith("data:"):
                        payload = line[len("data:") :].strip()
                        if not payload:
                            continue
                        # JSON 优先解析，否则按纯文本
                        try:
                            obj = json.loads(payload)
                            char_count += _count_text_in_json(obj)
                        except Exception:
                            char_count += len(payload)

            # 将块直接下发给客户端
            yield chunk
    finally:
        # 在流结束后进行扣费（允许负数，避免中途断流）
        try:
            # 处理缓冲中的尾行（若以 data: 开头且未换行）
            tail = buffer.strip()
            if tail.startswith("data:"):
                payload = tail[len("data:") :].strip()
                if payload:
                    try:
                        obj = json.loads(payload)
                        char_count += _count_text_in_json(obj)
                    except Exception:
                        char_count += len(payload)

            # 按字符计量直接传入 usage_amount（允许负数）
            PointService.consume_points(
                db=db,
                user_uid=user_uid,
                from_user_uid=from_user_uid,
                workflow_id=workflow_id,
                usage_amount=char_count,
                allow_negative=True,
                record_desc_prefix=f"流式扣费: workflow_id={workflow_id}",
            )
        except Exception:
            # 扣费失败不影响流式传输的完成（可在日志系统里记录）
            pass