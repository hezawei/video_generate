"""首次部署（Git版本）"""
import subprocess
from config import SERVER, REMOTE_DIR

# GitHub仓库地址（SSH方式，服务器已配置SSH Key）
REPO_URL = "git@github.com:hezawei/video_generate.git"

def run(cmd):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

print("=" * 50)
print("首次部署 (Git Clone)")
print("=" * 50)

# 1. 清理旧目录并克隆仓库
print("[1/3] 克隆仓库...")
run(f'ssh {SERVER} "rm -rf {REMOTE_DIR} && git clone {REPO_URL} {REMOTE_DIR}"')

# 2. 安装环境（分步执行，避免权限问题）
print("[2/3] 安装环境...")
# 修复脚本换行符和权限
run(f'ssh {SERVER} "cd {REMOTE_DIR} && chmod +x scripts/server/*.sh && sed -i \'s/\\r$//\' scripts/server/*.sh"')
# 创建venv并安装后端依赖
run(f'ssh {SERVER} "cd {REMOTE_DIR} && python3 -m venv venv && source venv/bin/activate && pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"')
# 安装前端依赖
run(f'ssh {SERVER} "cd {REMOTE_DIR}/frontend && npm config set registry https://registry.npmmirror.com && npm install"')
# 修复node_modules权限并构建
run(f'ssh {SERVER} "cd {REMOTE_DIR}/frontend && chmod -R +x node_modules/.bin/ && npm run build"')

# 3. 启动服务（production.py已在git仓库中）
print("[3/3] 启动服务...")
run(f'ssh {SERVER} "cd {REMOTE_DIR} && ./scripts/server/start.sh"')

print("=" * 50)
print("部署完成！")
