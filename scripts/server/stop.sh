#!/bin/bash
# 停止服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# scripts/server -> scripts -> project_root
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_DIR"

if [ -f server.pid ]; then
    PID=$(cat server.pid)
    if kill -0 "$PID" 2>/dev/null; then
        echo "正在停止服务 (PID: $PID)..."
        kill "$PID" 2>/dev/null
        # 等待进程退出，最多10秒
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        # 如果还没退出，强制杀死
        if kill -0 "$PID" 2>/dev/null; then
            echo "进程未响应，强制终止..."
            kill -9 "$PID" 2>/dev/null
        fi
    fi
    rm -f server.pid
    echo "服务已停止"
else
    echo "服务未运行"
fi
