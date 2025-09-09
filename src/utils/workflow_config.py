from typing import Dict

class WorkflowConfig:
    """
    工作流配置统一管理类
    集中管理所有workflow_id，便于维护和扩展
    """
    
    # 工作流ID映射表
    WORKFLOW_IDS: Dict[str, str] = {
        # 文案生成
        "copywriting": "7543079212585009195",
    }
    
    # 工作流名称映射（用于显示和日志）
    WORKFLOW_NAMES: Dict[str, str] = {
        "copywriting": "文案生成",
    }
    
    # 流式传输工作流
    STREAMING_WORKFLOWS = {
        "copywriting",
    }
    
    # 非流式传输工作流
    NON_STREAMING_WORKFLOWS = {
    }
    
    @classmethod
    def get_workflow_id(cls, workflow_key: str) -> str:
        """
        获取工作流ID
        
        Args:
            workflow_key: 工作流键名
        
        Returns:
            工作流ID
        
        Raises:
            KeyError: 如果工作流键名不存在
        """
        if workflow_key not in cls.WORKFLOW_IDS:
            raise KeyError(f"未找到工作流键名: {workflow_key}")
        return cls.WORKFLOW_IDS[workflow_key]
    
    @classmethod
    def get_workflow_name(cls, workflow_key: str) -> str:
        """
        获取工作流显示名称
        
        Args:
            workflow_key: 工作流键名
        
        Returns:
            工作流显示名称
        """
        return cls.WORKFLOW_NAMES.get(workflow_key, workflow_key)
    
    @classmethod
    def is_streaming_workflow(cls, workflow_key: str) -> bool:
        """
        判断是否为流式传输工作流
        
        Args:
            workflow_key: 工作流键名
        
        Returns:
            是否为流式传输工作流
        """
        return workflow_key in cls.STREAMING_WORKFLOWS
    
    @classmethod
    def get_all_workflow_keys(cls) -> list[str]:
        """
        获取所有工作流键名
        
        Returns:
            工作流键名列表
        """
        return list(cls.WORKFLOW_IDS.keys())
    
    @classmethod
    def get_streaming_workflow_keys(cls) -> list[str]:
        """
        获取所有流式传输工作流键名
        
        Returns:
            流式传输工作流键名列表
        """
        return list(cls.STREAMING_WORKFLOWS)
    
    @classmethod
    def get_non_streaming_workflow_keys(cls) -> list[str]:
        """
        获取所有非流式传输工作流键名
        
        Returns:
            非流式传输工作流键名列表
        """
        return list(cls.NON_STREAMING_WORKFLOWS)


# 便捷访问实例
workflow_config = WorkflowConfig()


# 便捷函数
def get_workflow_id(workflow_key: str) -> str:
    """
    获取工作流ID的便捷函数
    
    Args:
        workflow_key: 工作流键名
    
    Returns:
        工作流ID
    """
    return WorkflowConfig.get_workflow_id(workflow_key)


def get_workflow_name(workflow_key: str) -> str:
    """
    获取工作流名称的便捷函数
    
    Args:
        workflow_key: 工作流键名
    
    Returns:
        工作流显示名称
    """
    return WorkflowConfig.get_workflow_name(workflow_key)


def is_streaming_workflow(workflow_key: str) -> bool:
    """
    判断是否为流式传输工作流的便捷函数
    
    Args:
        workflow_key: 工作流键名
    
    Returns:
        是否为流式传输工作流
    """
    return WorkflowConfig.is_streaming_workflow(workflow_key)