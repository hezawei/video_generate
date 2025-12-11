"""仅更新后端（最快）"""
import os
import subprocess
from config import SERVER, REMOTE_DIR

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(cmd):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

print("更新后端...")

run(f'ssh {SERVER} "cd {REMOTE_DIR} && ./server/stop.sh 2>/dev/null || true"')
run(f'scp -r "{PROJECT_DIR}/backend" {SERVER}:{REMOTE_DIR}/')
run(f'ssh {SERVER} "cd {REMOTE_DIR} && ./server/start.sh"')

print("后端更新完成！")
