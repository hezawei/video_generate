#!/bin/bash
# 重启服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# scripts/server -> scripts -> project_root
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_DIR"

"$SCRIPT_DIR/stop.sh"
sleep 1
"$SCRIPT_DIR/start.sh"
