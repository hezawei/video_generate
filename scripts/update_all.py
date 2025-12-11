"""一键更新：本地提交 + 推送 + 服务器自动拉取"""
import subprocess
import os
from datetime import datetime
from config import SERVER, REMOTE_DIR

# 项目根目录
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(cmd, cwd=None):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd or PROJECT_DIR)

print("=" * 50)
print("一键更新")
print("=" * 50)

# 1. 本地 Git 操作
print("\n[1/4] 提交本地代码...")
run("git add .")
# commit message 使用当前时间
msg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# 如果没有变更，commit会失败，所以用 || true 忽略错误
run(f'git commit -m "{msg}" || echo "无新变更"')

print("\n[2/4] 推送到 GitHub...")
run("git push origin master")

# 2. 服务器更新
print("\n[3/4] 服务器拉取代码...")
# 记录旧HEAD，强制重置，然后传递旧HEAD给update.sh来检测变更
run(f'ssh {SERVER} "cd {REMOTE_DIR} && OLD_HEAD=$(git rev-parse HEAD) && git fetch origin && git reset --hard origin/master && bash scripts/server/update.sh $OLD_HEAD"')

print("\n" + "=" * 50)
print("更新完成！")
print("=" * 50)
