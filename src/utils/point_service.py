from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from crud.point_config import get_point_config_by_workflow_id
from crud.point_record import create_point_record
from crud.user import update_user_point
from db.point_config import PointConfig
from db.user import User
from utils.workflow_config import get_workflow_name
from .point_calculator import calculate_consumption, format_consumption_desc


class PointService:
    """
    积分服务层：统一封装积分预检、计算、扣减与记录
    """

    @staticmethod
    def check_non_streaming_workflow_points(db: Session, current_user: User, workflow_id: str) -> Optional[PointConfig]:
        """
        非流式工作流事前积分校验。
        - 如果绑定了积分配置且用户当前积分 <= 0，则阻断请求。
        - 返回启用的积分配置（若不存在则代表免费）。
        """
        cfg = get_point_config_by_workflow_id(db, workflow_id)
        if cfg and (current_user.point is None or current_user.point <= 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="积分不足，无法执行该操作"
            )
        return cfg

    @staticmethod
    def check_streaming_workflow_points(db: Session, current_user: User, workflow_id: str) -> Optional[PointConfig]:
        """
        流式工作流事前积分校验。
        - 规则同非流式：若绑定了积分配置且用户当前积分 <= 0，则阻断。
        - 流式扣费在流结束后进行（允许负数）。
        """
        cfg = get_point_config_by_workflow_id(db, workflow_id)
        if cfg and (current_user.point is None or current_user.point <= 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="积分不足，无法开始流式任务"
            )
        return cfg

    @staticmethod
    def calculate(db: Session, workflow_id: str, usage_amount: Optional[int]) -> Tuple[int, str, Optional[PointConfig]]:
        """
        计算扣费金额并生成说明。
        - 返回 (总扣费积分, 描述, 配置对象)
        - 未配置或配置未启用，返回 0 且描述为免费。
        """
        cfg = get_point_config_by_workflow_id(db, workflow_id)
        if not cfg or cfg.is_enable != 1:
            return 0, "免费使用，无积分扣减", None

        total = calculate_consumption(cfg.consume, cfg.measure_unit, usage_amount)
        desc = format_consumption_desc(
            cfg.function_name or get_workflow_name(cfg.function_id) if hasattr(cfg, 'function_id') else (cfg.function_name or workflow_id),
            cfg.consume,
            cfg.measure_unit,
            usage_amount,
            total,
        )
        return total, desc, cfg

    @staticmethod
    def consume_points(
        db: Session,
        user_uid: str,
        from_user_uid: Optional[str],
        workflow_id: str,
        usage_amount: Optional[int],
        allow_negative: bool = False,
        record_type: int = 2,
        record_desc_prefix: Optional[str] = None,
    ) -> dict:
        """
        统一扣减入口：根据 workflow_id 及使用量扣减积分并记录流水。
        - 非配置或未启用：直接返回免费结果。
        - 扣减：更新用户积分（负数表示扣减），插入积分记录（正数表示消耗）。
        """
        total, desc, cfg = PointService.calculate(db, workflow_id, usage_amount)
        if total <= 0:
            return {"is_free": True, "consumption": 0, "desc": "免费使用，无积分扣减"}

        # 扣减用户积分：消耗用负值更新
        update_user_point(db, user_uid=user_uid, point_delta=-total, allow_negative=allow_negative)

        final_desc = f"{record_desc_prefix}，{desc}" if record_desc_prefix else desc
        create_point_record(
            db,
            user_uid=user_uid,
            from_user_uid=from_user_uid or user_uid,
            point=total,
            record_type=record_type,
            record_desc=final_desc,
        )
        return {"is_free": False, "consumption": total, "desc": final_desc}

    @staticmethod
    def consume_points_by_response(
        db: Session,
        user_uid: str,
        from_user_uid: Optional[str],
        workflow_id: str,
        response_text: str,
        allow_negative: bool = False,
        record_desc_prefix: Optional[str] = None,
    ) -> dict:
        """
        按响应文本内容长度进行扣费（适用于按字符计费）。
        - 其他单位（按次、按分钟）可通过 usage_amount=1 或秒数调用 consume_points。
        """
        usage_amount = len(response_text or "")
        return PointService.consume_points(
            db,
            user_uid,
            from_user_uid,
            workflow_id,
            usage_amount,
            allow_negative=allow_negative,
            record_type=2,
            record_desc_prefix=record_desc_prefix,
        )