#!/bin/bash
# 服务器端：自动更新脚本
# 用法: bash scripts/server/update.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[1/3] 构建前端...${NC}"
cd frontend
npm install --silent
npm run build
cd ..

echo -e "${YELLOW}[2/3] 更新后端依赖...${NC}"
source venv/bin/activate
pip install -r backend/requirements.txt --quiet -i https://pypi.tuna.tsinghua.edu.cn/simple

echo -e "${YELLOW}[3/3] 重启服务...${NC}"
bash scripts/server/restart.sh

echo -e "${GREEN}更新完成！${NC}"
