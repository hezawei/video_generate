#!/bin/bash
# 服务器端：自动更新脚本
# 用法: ./scripts/server/update.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[1/4] 拉取最新代码...${NC}"
# 记录当前commit
OLD_HEAD=$(git rev-parse HEAD 2>/dev/null || echo "none")
# 丢弃本地修改，强制拉取
git fetch origin
git reset --hard origin/master
NEW_HEAD=$(git rev-parse HEAD)

echo -e "${YELLOW}[2/4] 检查前端变更...${NC}"
# 比较前后commit，检查是否有frontend变更
if [ "$OLD_HEAD" = "none" ] || [ "$OLD_HEAD" != "$NEW_HEAD" ]; then
    if git diff --name-only "$OLD_HEAD" "$NEW_HEAD" 2>/dev/null | grep -q "^frontend/"; then
        echo "发现前端变更，重新构建..."
        cd frontend
        npm install
        npm run build
        cd ..
    else
        echo "前端无变更，跳过构建。"
    fi
else
    echo "代码无变更。"
fi

echo -e "${YELLOW}[3/4] 更新后端依赖...${NC}"
source venv/bin/activate
pip install -r backend/requirements.txt --quiet -i https://pypi.tuna.tsinghua.edu.cn/simple

echo -e "${YELLOW}[4/4] 重启服务...${NC}"
bash scripts/server/restart.sh

echo -e "${GREEN}更新完成！${NC}"
