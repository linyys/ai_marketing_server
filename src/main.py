import os
import sys
import logging
import traceback
from datetime import datetime

parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)

from fastapi import FastAPI, Request, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from utils.exceptions import BaseAPIException, format_error_response

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Marketing Server", description="AI营销服务器API", version="1.0.0"
)

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    error_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 记录详细错误信息
    logger.error(
        f"Error ID: {error_id} | "
        f"URL: {request.url} | "
        f"Method: {request.method} | "
        f"Error: {str(exc)} | "
        f"Traceback: {traceback.format_exc()}"
    )
    
    # 返回用户友好的错误信息
    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "message": "服务器遇到了一个错误，请稍后重试",
            "error_id": error_id,
            "detail": str(exc) if app.debug else None
        }
    )

@app.exception_handler(BaseAPIException)
async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """自定义API异常处理器"""
    logger.warning(
        f"API Exception | "
        f"URL: {request.url} | "
        f"Method: {request.method} | "
        f"Status: {exc.status_code} | "
        f"Error Code: {exc.error_code} | "
        f"Detail: {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(exc)
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    logger.warning(
        f"HTTP Exception | "
        f"URL: {request.url} | "
        f"Method: {request.method} | "
        f"Status: {exc.status_code} | "
        f"Detail: {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求"""
    start_time = datetime.now()
    
    # 记录请求信息
    logger.info(
        f"Request | "
        f"Method: {request.method} | "
        f"URL: {request.url} | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        
        # 记录响应信息
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Response | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.3f}s | "
            f"URL: {request.url}"
        )
        
        return response
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"Request Failed | "
            f"Time: {process_time:.3f}s | "
            f"URL: {request.url} | "
            f"Error: {str(e)}"
        )
        raise
from modules.admin.router import router as admin_router
from modules.copywriting_types.router import router as copywriting_type_router
from modules.user.router import router as user_router
from modules.knowledge.router import router as knowledge_router
from modules.coze.router import router as coze_router
from modules.robot.router import router as robot_router
from modules.douyin.router import router as douyin_router
from modules.scheduled_tasks.router import router as scheduled_tasks_router
app.include_router(admin_router, prefix="/api")
app.include_router(copywriting_type_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
app.include_router(coze_router, prefix="/api")
app.include_router(robot_router, prefix="/api")
app.include_router(douyin_router, prefix="/api")
app.include_router(scheduled_tasks_router, prefix="/api")

# 挂载静态文件目录
BASE_DIR = Path(__file__).resolve().parent

# 静态资源
app.mount("/static", StaticFiles(directory=BASE_DIR / "resource"), name="static")

# 用户上传的文件
uploads_dir = BASE_DIR / "uploads"
uploads_dir.mkdir(exist_ok=True)  # 确保目录存在
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api_docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/api_doc/swagger-ui-bundle.js",
        swagger_css_url="/static/api_doc/swagger-ui.css",
    )


@app.get("/", response_class=HTMLResponse)
def welcome():
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <title>AI营销智能体</title>
        <style>
          body{font-family:Arial,Helvetica,sans-serif;background:#f4f7fa;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
          .card{background:#fff;padding:40px 60px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.08);text-align:center}
          h1{color:#165dff;margin-bottom:8px}
          p{color:#666}
          a{color:#165dff;text-decoration:none}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>AI营销服务器</h1>
          <p>🚀 服务已启动，欢迎使用！</p>
          <p><a href="/api_docs">📖 Swagger 文档</a> | <a href="/redoc">📘 ReDoc 文档</a></p>
        </div>
      </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    dev = "127.0.0.1"
    pre = "192.168.0.44"
    
    uvicorn.run(
        "main:app",
        host=pre,
        port=8001,
        reload=True,
        workers=1,
        timeout_keep_alive=300,
        timeout_graceful_shutdown=300,
        limit_concurrency=100,
        backlog=2048,
    )
