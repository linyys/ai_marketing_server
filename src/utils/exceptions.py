from fastapi import HTTPException, status
from typing import Optional, Any, Dict


class BaseAPIException(HTTPException):
    """基础API异常类"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class ValidationException(BaseAPIException):
    """数据验证异常"""
    
    def __init__(self, detail: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )


class AuthenticationException(BaseAPIException):
    """认证异常"""
    
    def __init__(self, detail: str = "认证失败", error_code: str = "AUTH_ERROR"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code
        )


class AuthorizationException(BaseAPIException):
    """授权异常"""
    
    def __init__(self, detail: str = "权限不足", error_code: str = "PERMISSION_DENIED"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code
        )


class NotFoundException(BaseAPIException):
    """资源未找到异常"""
    
    def __init__(self, detail: str = "资源未找到", error_code: str = "NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code
        )


class ConflictException(BaseAPIException):
    """资源冲突异常"""
    
    def __init__(self, detail: str = "资源冲突", error_code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code
        )


class BusinessException(BaseAPIException):
    """业务逻辑异常"""
    
    def __init__(self, detail: str, error_code: str = "BUSINESS_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code
        )


class DatabaseException(BaseAPIException):
    """数据库异常"""
    
    def __init__(self, detail: str = "数据库操作失败", error_code: str = "DATABASE_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code
        )


class ExternalServiceException(BaseAPIException):
    """外部服务异常"""
    
    def __init__(self, detail: str = "外部服务不可用", error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code=error_code
        )


def format_error_response(exc: BaseAPIException) -> Dict[str, Any]:
    """格式化错误响应"""
    return {
        "error": True,
        "error_code": exc.error_code,
        "message": exc.detail,
        "status_code": exc.status_code
    }