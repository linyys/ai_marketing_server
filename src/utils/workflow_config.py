from typing import Dict, TypedDict

class WorkflowInfo(TypedDict):
    """工作流信息结构"""
    function: str  # 工作流功能
    name: str      # 工作流名称
    is_streaming: bool  # 是否流式传输

class WorkflowConfig:
    """
    工作流配置统一管理类
    使用统一的键值对结构管理所有工作流配置
    """
    
    # 统一的工作流配置映射表
    WORKFLOWS: Dict[str, WorkflowInfo] = {
        "7543079212585009195": {
            "function": "copywriting",
            "name": "文案生成",
            "is_streaming": True
        }
    }
    
    @classmethod
    def get_workflow_info(cls, workflow_id: str) -> WorkflowInfo:
        """
        获取工作流信息
        
        Args:
            workflow_id: 工作流ID
        
        Returns:
            工作流信息
        
        Raises:
            KeyError: 如果工作流ID不存在
        """
        if workflow_id not in cls.WORKFLOWS:
            raise KeyError(f"未找到工作流ID: {workflow_id}")
        return cls.WORKFLOWS[workflow_id]
    
    @classmethod
    def get_workflow_by_function(cls, function: str) -> tuple[str, WorkflowInfo]:
        """
        根据功能获取工作流ID和信息
        
        Args:
            function: 工作流功能名称
        
        Returns:
            (工作流ID, 工作流信息)
        
        Raises:
            KeyError: 如果功能不存在
        """
        for workflow_id, info in cls.WORKFLOWS.items():
            if info["function"] == function:
                return workflow_id, info
        raise KeyError(f"未找到功能: {function}")
    
    @classmethod
    def get_workflow_name(cls, workflow_id: str) -> str:
        """
        获取工作流显示名称
        
        Args:
            workflow_id: 工作流ID
        
        Returns:
            工作流显示名称
        """
        info = cls.get_workflow_info(workflow_id)
        return info["name"]
    
    @classmethod
    def is_streaming_workflow(cls, workflow_id: str) -> bool:
        """
        判断是否为流式传输工作流
        
        Args:
            workflow_id: 工作流ID
        
        Returns:
            是否为流式传输工作流
        """
        info = cls.get_workflow_info(workflow_id)
        return info["is_streaming"]
    
    @classmethod
    def get_all_workflow_ids(cls) -> list[str]:
        """
        获取所有工作流ID
        
        Returns:
            工作流ID列表
        """
        return list(cls.WORKFLOWS.keys())
    
    @classmethod
    def get_streaming_workflow_ids(cls) -> list[str]:
        """
        获取所有流式传输工作流ID
        
        Returns:
            流式传输工作流ID列表
        """
        return [workflow_id for workflow_id, info in cls.WORKFLOWS.items() if info["is_streaming"]]
    
    @classmethod
    def get_non_streaming_workflow_ids(cls) -> list[str]:
        """
        获取所有非流式传输工作流ID
        
        Returns:
            非流式传输工作流ID列表
        """
        return [workflow_id for workflow_id, info in cls.WORKFLOWS.items() if not info["is_streaming"]]
    
    @classmethod
    def get_workflows_by_function(cls, function: str) -> list[tuple[str, WorkflowInfo]]:
        """
        根据功能获取所有匹配的工作流
        
        Args:
            function: 工作流功能名称
        
        Returns:
            匹配的工作流列表 [(工作流ID, 工作流信息)]
        """
        return [(workflow_id, info) for workflow_id, info in cls.WORKFLOWS.items() if info["function"] == function]


# 便捷访问实例
workflow_config = WorkflowConfig()


# 便捷函数
def get_workflow_id_by_function(function: str) -> str:
    """
    根据功能获取工作流ID的便捷函数
    
    Args:
        function: 工作流功能名称
    
    Returns:
        工作流ID
    """
    workflow_id, _ = WorkflowConfig.get_workflow_by_function(function)
    return workflow_id


def get_workflow_info(workflow_id: str) -> WorkflowInfo:
    """
    获取工作流信息的便捷函数
    
    Args:
        workflow_id: 工作流ID
    
    Returns:
        工作流信息
    """
    return WorkflowConfig.get_workflow_info(workflow_id)


def get_workflow_name(workflow_id: str) -> str:
    """
    获取工作流名称的便捷函数
    
    Args:
        workflow_id: 工作流ID
    
    Returns:
        工作流显示名称
    """
    return WorkflowConfig.get_workflow_name(workflow_id)


def is_streaming_workflow(workflow_id: str) -> bool:
    """
    判断是否为流式传输工作流的便捷函数
    
    Args:
        workflow_id: 工作流ID
    
    Returns:
        是否为流式传输工作流
    """
    return WorkflowConfig.is_streaming_workflow(workflow_id)


# 向后兼容的函数（已废弃，建议使用新的API）
def get_workflow_id(workflow_key: str) -> str:
    """
    获取工作流ID的便捷函数（已废弃）
    
    Args:
        workflow_key: 工作流功能名称
    
    Returns:
        工作流ID
    
    Deprecated:
        请使用 get_workflow_id_by_function 替代
    """
    return get_workflow_id_by_function(workflow_key)