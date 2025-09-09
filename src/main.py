import os
import sys
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)

from fastapi import FastAPI
from modules.user.router import router as user_router
from modules.admin.router import router as admin_router
from modules.copywriting_type.router import router as copywriting_type_router
from modules.knowledge.router import router as knowledge_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(
    title="AI Marketing Server",
    description="AI营销服务器API",
    version="1.0.0"
)

# 注册用户模块路由
app.include_router(user_router, prefix="/user")

# 注册管理员模块路由
app.include_router(admin_router, prefix="/api")

# 注册文案类型模块路由
app.include_router(copywriting_type_router, prefix="/copywriting_type")

# 注册知识库模块路由
app.include_router(knowledge_router, prefix="/api")

# 挂载静态文件目录
BASE_DIR = Path(__file__).resolve().parent

# 挂载resource目录（原有的静态资源）
app.mount("/static", StaticFiles(directory=BASE_DIR / "resource"), name="static")

# 挂载新的uploads目录（用户上传的文件）
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
          <p><a href="/docs">📖 Swagger 文档</a> | <a href="/redoc">📘 ReDoc 文档</a></p>
        </div>
      </body>
    </html>
    """



if __name__ == "__main__":
    import uvicorn
    dev = "127.0.0.1"
    pre = "192.168.0.44"

    uvicorn.run(
        'main:app', 
        host=pre, 
        port=8000, 
        reload=True, 
        workers=1,
        timeout_keep_alive=300, 
        timeout_graceful_shutdown=300, 
        limit_concurrency=100,
        backlog=2048
    )
  
