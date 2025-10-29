from typing import Optional
import math
from decimal import Decimal, ROUND_UP, ROUND_HALF_UP

# 计量单位常量
class MeasureUnit:
    NONE = 0          # 未计费/未配置
    CHAR = 1          # 每字符
    PER_CALL = 2      # 每次调用
    PER_MINUTE = 3    # 每分钟（按分钟向上取整）


def unit_name(unit: int) -> str:
    if unit == MeasureUnit.CHAR:
        return "每字符"
    if unit == MeasureUnit.PER_CALL:
        return "每次调用"
    if unit == MeasureUnit.PER_MINUTE:
        return "每分钟"
    return "未计费"


def unit_short_label(unit: int) -> str:
    """用于规则描述中的短标签，不包含“每”。"""
    if unit == MeasureUnit.CHAR:
        return "字符"
    if unit == MeasureUnit.PER_CALL:
        return "次调用"
    if unit == MeasureUnit.PER_MINUTE:
        return "分钟"
    return "未计费"


def calculate_consumption(token: Decimal, measure_unit: int, unit: int, usage_amount: Optional[int]) -> Decimal:
    """
    新版计费计算器：
    - measure_unit=1(每字符): usage_amount 为字符数，次数 = ceil((usage_amount or 0) / unit)，总消耗 = 次数 * token
    - measure_unit=2(每次调用): usage_amount 为调用次数（默认1），次数 = ceil((usage_amount or 1) / unit)，总消耗 = 次数 * token
    - measure_unit=3(每分钟): usage_amount 为秒数，分钟 = max(1, ceil(seconds/60))，次数 = ceil(分钟 / unit)，总消耗 = 次数 * token
    - measure_unit=0: 未计费/未配置，返回 0（兼容旧配置）。
    - 若计量单位缺失（None），按系统默认“每字符”(1) 处理。
    结果以 Decimal 返回，不再向上取整为整数；统一量化到 6 位小数。
    """
    try:
        t = Decimal(token or 0)
    except Exception:
        t = Decimal(0)
    if t <= 0:
        return Decimal('0')

    u = int(unit or 1)
    if u <= 0:
        u = 1

    # 缺失则按默认“每字符”；保留旧值0（未计费）
    mu = int(measure_unit) if measure_unit is not None else MeasureUnit.CHAR

    if mu == MeasureUnit.NONE:
        return Decimal('0')

    if mu == MeasureUnit.PER_CALL:
        calls = int(usage_amount or 1)
        batches = math.ceil(calls / u)
        total = (t * Decimal(batches)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        return total

    if mu == MeasureUnit.CHAR:
        count = int(usage_amount or 0)
        if count <= 0:
            return Decimal('0')
        batches = math.ceil(count / u)
        total = (t * Decimal(batches)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        return total

    if mu == MeasureUnit.PER_MINUTE:
        seconds = int(usage_amount or 0)
        minutes = max(1, math.ceil(seconds / 60)) if seconds > 0 else 1
        batches = math.ceil(minutes / u)
        total = (t * Decimal(batches)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        return total

    return Decimal('0')


def format_consumption_desc(function_name: str, token: Decimal, measure_unit: int, unit: int, usage_amount: Optional[int], total_cost: Decimal) -> str:
    """
    生成人类可读的扣费说明（新版）。
    例如："工作流: 文案创作 | 计费: 每字符 | 规则: 每100字符消耗10 | 计量: 128 | 扣减: 20积分"
    """
    mu = int(measure_unit) if measure_unit is not None else MeasureUnit.CHAR
    unit_label = unit_name(mu)
    short_label = unit_short_label(mu)
    usage = int(usage_amount or 0)
    token_str = str(Decimal(token or 0).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP).normalize())
    total_str = str(Decimal(total_cost or 0).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP).normalize())
    return (
        f"工作流: {function_name} | 计费: {unit_label} | 规则: 每{unit}{short_label}消耗{token_str} | "
        f"计量: {usage} | 扣减: {total_str}积分"
    )