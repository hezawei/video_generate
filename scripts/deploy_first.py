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

# 2. 执行安装脚本
print("[2/3] 安装环境（需要几分钟）...")
run(f'ssh {SERVER} "cd {REMOTE_DIR} && chmod +x scripts/server/*.sh && ./scripts/server/install.sh"')

# 3. 启动服务
print("[3/3] 启动服务...")
run(f'ssh {SERVER} "cd {REMOTE_DIR} && ./scripts/server/start.sh"')

print("=" * 50)
print("部署完成！")
