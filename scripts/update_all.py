"""完整更新（前端+后端）"""
import os
import subprocess
from config import SERVER, REMOTE_DIR

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(cmd):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

print("完整更新...")

run(f'ssh {SERVER} "cd {REMOTE_DIR} && ./server/stop.sh 2>/dev/null || true"')
run(f'scp -r "{PROJECT_DIR}/backend" {SERVER}:{REMOTE_DIR}/')
run(f'scp -r "{PROJECT_DIR}/frontend/src" "{PROJECT_DIR}/frontend/index.html" "{PROJECT_DIR}/frontend/package.json" "{PROJECT_DIR}/frontend/vite.config.ts" "{PROJECT_DIR}/frontend/tailwind.config.js" "{PROJECT_DIR}/frontend/tsconfig.json" "{PROJECT_DIR}/frontend/postcss.config.js" {SERVER}:{REMOTE_DIR}/frontend/')
run(f'ssh {SERVER} "cd {REMOTE_DIR}/frontend && npm run build"')
run(f'ssh {SERVER} "cd {REMOTE_DIR} && ./server/start.sh"')

print("更新完成！")
