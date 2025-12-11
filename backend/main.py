"""
FastAPI 主入口
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db
from routes import sessions, generate
from config import SERVER_CONFIG
from tasks.task_recovery import start_recovery_daemon

# 创建FastAPI应用
app = FastAPI(
    title="AI视频生成",
    description="个人用AI视频生成服务",
    version="1.0.0"
)

# CORS配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(sessions.router)
app.include_router(generate.router)

# 静态文件服务（上传的图片和下载的视频）
uploads_dir = SERVER_CONFIG["uploads_dir"]
downloads_dir = SERVER_CONFIG["downloads_dir"]
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(downloads_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/downloads", StaticFiles(directory=downloads_dir), name="downloads")


@app.on_event("startup")
def startup():
    """应用启动时初始化数据库并启动任务守护线程"""
    init_db()
    # 启动任务恢复守护线程
    start_recovery_daemon()


@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        reload=True
    )
