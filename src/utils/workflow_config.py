from typing import Dict, List, TypedDict

class WorkflowInfo(TypedDict):
    """工作流信息结构"""
    workflow_id: str   # 工作流ID
    name: str          # 工作流名称
    is_streaming: bool # 是否流式传输

class WorkflowConfig:
    """
    工作流配置统一管理类
    使用工作流功能作为键的统一配置结构
    """
    
    # 以工作流功能为键的配置映射表
    WORKFLOWS: Dict[str, WorkflowInfo] = {
        "copywriting_create": {
            "workflow_id": "7548632031845728291",
            "name": "文案创作",
            "is_streaming": True
        },
        "prompt_generate": {
            "workflow_id": "7548335440656662571",
            "name": "提示词生成",
            "is_streaming": False
        },
        "video_market_analysis": {
            "workflow_id": "7545291455734005806",
            "name": "个人主页内容分析",
            "is_streaming": True
        },
        "video_to_text": {
            "workflow_id": "7517866010540654646",
            "name": "视频转文字",
            "is_streaming": False
        },
        "market_analysis": {
            "workflow_id": "7561643194401210411",
            "name": "市场分析",
            "is_streaming": True
        }
    }
    
    @classmethod
    def get_workflow_info(cls, function: str) -> WorkflowInfo:
        """
        根据工作流功能获取工作流信息
        
        Args:
            function: 工作流功能
            
        Returns:
            WorkflowInfo: 工作流信息
            
        Raises:
            KeyError: 如果功能不存在
        """
        if function not in cls.WORKFLOWS:
            raise KeyError(f"未找到功能: {function}")
        return cls.WORKFLOWS[function]
    
    @classmethod
    def get_workflow_id(cls, function: str) -> str:
        """
        根据功能获取工作流ID
        
        Args:
            function: 工作流功能
            
        Returns:
            str: 工作流ID
            
        Raises:
            KeyError: 如果功能不存在
        """
        info = cls.get_workflow_info(function)
        return info["workflow_id"]
    
    @classmethod
    def get_workflow_name(cls, function: str) -> str:
        """
        根据工作流功能获取工作流名称
        
        Args:
            function: 工作流功能
            
        Returns:
            str: 工作流名称
        """
        info = cls.get_workflow_info(function)
        return info["name"]
    
    @classmethod
    def is_streaming_workflow(cls, function: str) -> bool:
        """
        判断工作流是否为流式传输
        
        Args:
            function: 工作流功能
            
        Returns:
            bool: 是否为流式传输
        """
        info = cls.get_workflow_info(function)
        return info["is_streaming"]
    
    @classmethod
    def get_all_functions(cls) -> List[str]:
        """
        获取所有工作流功能
        
        Returns:
            List[str]: 所有工作流功能列表
        """
        return list(cls.WORKFLOWS.keys())
    
    @classmethod
    def get_streaming_functions(cls) -> List[str]:
        """
        获取所有流式传输工作流功能
        
        Returns:
            List[str]: 流式传输工作流功能列表
        """
        return [function for function, info in cls.WORKFLOWS.items() 
                if info["is_streaming"]]
    
    @classmethod
    def get_non_streaming_functions(cls) -> List[str]:
        """
        获取所有非流式传输工作流功能
        
        Returns:
            List[str]: 非流式传输工作流功能列表
        """
        return [function for function, info in cls.WORKFLOWS.items() 
                if not info["is_streaming"]]
    
# 便捷函数
def get_workflow_id(function: str) -> str:
    """
    根据功能获取工作流ID
    
    Args:
        function: 工作流功能
        
    Returns:
        str: 工作流ID
    """
    return WorkflowConfig.get_workflow_id(function)

def get_workflow_info(function: str) -> WorkflowInfo:
    """
    根据功能获取工作流信息
    
    Args:
        function: 工作流功能
        
    Returns:
        WorkflowInfo: 工作流信息
    """
    return WorkflowConfig.get_workflow_info(function)

def get_workflow_name(function: str) -> str:
    """
    根据功能获取工作流名称
    
    Args:
        function: 工作流功能
        
    Returns:
        str: 工作流名称
    """
    return WorkflowConfig.get_workflow_name(function)

def is_streaming_workflow(function: str) -> bool:
    """
    根据功能判断是否为流式传输工作流
    
    Args:
        function: 工作流功能
        
    Returns:
        bool: 是否为流式传输
    """
    return WorkflowConfig.is_streaming_workflow(function)

# 向后兼容函数
def get_workflow_id_by_function(function: str) -> str:
    """
    @deprecated 请使用 get_workflow_id
    """
    return get_workflow_id(function)
