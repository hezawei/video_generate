#!/bin/bash
# 启动服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

source venv/bin/activate
cd backend
nohup python production.py > ../server.log 2>&1 &
echo $! > ../server.pid

echo "服务已启动，PID: $(cat ../server.pid)"
echo "访问地址: http://$(hostname -I | awk '{print $1}'):8002"
