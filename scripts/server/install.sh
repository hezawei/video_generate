#!/bin/bash
# 服务器端：首次安装/重装脚本
# 用法: ./scripts/server/install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_DIR"
echo "工作目录: $PROJECT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[1/5] 更新系统并安装依赖...${NC}"
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y python3 python3-pip python3-venv git curl

# 安装Node.js 18.x (Ubuntu apt的版本太旧)
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'.' -f1 | tr -d 'v')" -lt 16 ]; then
    echo "安装 Node.js 18.x..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
fi
echo "Node.js 版本: $(node -v)"

echo -e "${YELLOW}[2/5] 创建Python虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo -e "${YELLOW}[3/5] 安装后端依赖...${NC}"
# 使用清华镜像加速
pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo -e "${YELLOW}[4/5] 安装前端依赖...${NC}"
cd frontend
# 使用淘宝镜像加速
npm config set registry https://registry.npmmirror.com
npm install

echo -e "${YELLOW}[5/5] 构建前端...${NC}"
npm run build
cd ..

# 创建生产环境启动文件
cat > backend/production.py << 'PYEOF'
"""生产环境启动脚本"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db
from routes import sessions, generate
from config import SERVER_CONFIG
from tasks.task_recovery import start_recovery_daemon

app = FastAPI(title="AI视频生成")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(generate.router)

uploads_dir = SERVER_CONFIG["uploads_dir"]
downloads_dir = SERVER_CONFIG["downloads_dir"]
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(downloads_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/downloads", StaticFiles(directory=downloads_dir), name="downloads")
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

@app.on_event("startup")
def startup():
    init_db()
    start_recovery_daemon()

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse(os.path.join(frontend_dist, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("production:app", host="0.0.0.0", port=SERVER_CONFIG["port"], workers=2)
PYEOF

chmod +x scripts/server/*.sh
echo -e "${GREEN}安装完成！${NC}"
