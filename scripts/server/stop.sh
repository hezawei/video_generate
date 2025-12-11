#!/bin/bash
# 停止服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

if [ -f server.pid ]; then
    kill $(cat server.pid) 2>/dev/null
    rm server.pid
    echo "服务已停止"
else
    echo "服务未运行"
fi
