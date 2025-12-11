#!/bin/bash
# 启动服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# scripts/server -> scripts -> project_root
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_DIR"

# 确保没有残留进程
if [ -f server.pid ]; then
    OLD_PID=$(cat server.pid)
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "服务已在运行 (PID: $OLD_PID)，先停止..."
        kill "$OLD_PID" 2>/dev/null
        sleep 2
    fi
    rm -f server.pid
fi

source venv/bin/activate
cd backend
nohup python production.py > ../server.log 2>&1 &
echo $! > ../server.pid

sleep 1
if kill -0 $(cat ../server.pid) 2>/dev/null; then
    echo "服务已启动，PID: $(cat ../server.pid)"
    echo "访问地址: http://$(hostname -I | awk '{print $1}'):8002"
else
    echo "启动失败！查看日志: tail -f server.log"
    exit 1
fi
