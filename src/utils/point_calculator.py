from typing import Optional, Tuple
import math

# 计量单位常量
class MeasureUnit:
    CHAR = 0          # 按字符计费
    PER_CALL = 1      # 按次计费
    PER_MINUTE = 2    # 按分钟计费（向上取整）


def unit_name(unit: int) -> str:
    if unit == MeasureUnit.CHAR:
        return "按字符"
    if unit == MeasureUnit.PER_CALL:
        return "按次"
    if unit == MeasureUnit.PER_MINUTE:
        return "按分钟"
    return "未知单位"


def calculate_consumption(consume_per_unit: int, measure_unit: int, usage_amount: Optional[int]) -> int:
    """
    统一的计费计算器。
    - CHAR: usage_amount 为字符数，消耗 = consume_per_unit * usage_amount
    - PER_CALL: 不需要 usage_amount，消耗 = consume_per_unit
    - PER_MINUTE: usage_amount 为秒数或毫秒换算后的秒数，按分钟向上取整，消耗 = consume_per_unit * max(1, ceil(usage_amount / 60))
    """
    if consume_per_unit <= 0:
        return 0

    if measure_unit == MeasureUnit.PER_CALL:
        return consume_per_unit

    if measure_unit == MeasureUnit.CHAR:
        count = int(usage_amount or 0)
        if count <= 0:
            return 0
        return consume_per_unit * count

    if measure_unit == MeasureUnit.PER_MINUTE:
        seconds = int(usage_amount or 0)
        minutes = max(1, math.ceil(seconds / 60)) if seconds > 0 else 1
        return consume_per_unit * minutes

    return 0


def format_consumption_desc(function_name: str, consume_per_unit: int, measure_unit: int, usage_amount: Optional[int], total_cost: int) -> str:
    """
    生成人类可读的扣费说明。
    例如："工作流: 文案创作 | 计费: 按字符 | 单价: 1 | 计量: 128 | 扣减: 128积分"
    """
    unit_label = unit_name(measure_unit)
    usage = int(usage_amount or 0)
    return (
        f"工作流: {function_name} | 计费: {unit_label} | 单价: {consume_per_unit} | "
        f"计量: {usage} | 扣减: {total_cost}积分"
    )