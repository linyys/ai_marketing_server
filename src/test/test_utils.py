#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试工具类
"""

import json
from typing import Any, Dict, Optional
from fastapi.testclient import TestClient

class TestFormatter:
    """测试结果格式化器"""
    
    @staticmethod
    def format_test_result(
        route: str,
        method: str,
        input_params: Dict[str, Any],
        response: Any,
        expected_status: int = 200,
        test_name: str = "",
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        格式化测试结果
        
        Args:
            route: 测试的路由
            method: HTTP方法
            input_params: 输入参数
            response: 响应对象
            expected_status: 期望的状态码
            test_name: 测试名称
            headers: 请求头
        
        Returns:
            格式化的测试结果
        """
        is_passed = response.status_code == expected_status
        error_reason = None
        output_params = None
        
        try:
            output_params = response.json() if response.content else {}
        except:
            output_params = {"raw_content": response.text}
        
        if not is_passed:
            error_reason = f"状态码不匹配: 期望 {expected_status}, 实际 {response.status_code}"
            if response.content:
                try:
                    error_detail = response.json()
                    if "detail" in error_detail:
                        error_reason += f", 错误详情: {error_detail['detail']}"
                except:
                    error_reason += f", 响应内容: {response.text}"
        
        result = {
            "test_name": test_name,
            "route": f"{method.upper()} {route}",
            "is_passed": is_passed,
            "error_reason": error_reason,
            "input_params": {
                "body": input_params.get("json", {}),
                "query": input_params.get("params", {}),
                "headers": headers or {}
            },
            "output_params": {
                "status_code": response.status_code,
                "body": output_params,
                "headers": dict(response.headers)
            }
        }
        
        return result
    
    @staticmethod
    def print_test_result(result: Dict[str, Any]):
        """打印格式化的测试结果"""
        print("\n" + "="*80)
        print(f"测试名称: {result['test_name']}")
        print(f"测试路由: {result['route']}")
        print(f"是否通过: {'✅ 通过' if result['is_passed'] else '❌ 失败'}")
        
        if result['error_reason']:
            print(f"错误原因: {result['error_reason']}")
        
        print(f"输入参数: {json.dumps(result['input_params'], ensure_ascii=False, indent=2)}")
        print(f"输出参数: {json.dumps(result['output_params'], ensure_ascii=False, indent=2)}")
        print("="*80)

def make_request_with_format(
    client: TestClient,
    method: str,
    route: str,
    test_name: str,
    expected_status: int = 200,
    json_data: Optional[Dict] = None,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    发送请求并格式化结果
    
    Args:
        client: TestClient实例
        method: HTTP方法
        route: 路由
        test_name: 测试名称
        expected_status: 期望状态码
        json_data: JSON数据
        params: 查询参数
        headers: 请求头
    
    Returns:
        格式化的测试结果
    """
    input_params = {}
    if json_data:
        input_params["json"] = json_data
    if params:
        input_params["params"] = params
    
    # 发送请求
    if method.upper() == "GET":
        response = client.get(route, params=params, headers=headers)
    elif method.upper() == "POST":
        response = client.post(route, json=json_data, params=params, headers=headers)
    elif method.upper() == "PUT":
        response = client.put(route, json=json_data, params=params, headers=headers)
    elif method.upper() == "DELETE":
        response = client.delete(route, params=params, headers=headers)
    else:
        raise ValueError(f"不支持的HTTP方法: {method}")
    
    # 格式化结果
    result = TestFormatter.format_test_result(
        route=route,
        method=method,
        input_params=input_params,
        response=response,
        expected_status=expected_status,
        test_name=test_name,
        headers=headers
    )
    
    # 打印结果
    TestFormatter.print_test_result(result)
    
    return result