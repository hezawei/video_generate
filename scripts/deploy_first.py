"""首次部署"""
import os
import subprocess
from config import SERVER, SERVER_IP, SERVER_PORT, REMOTE_DIR

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(cmd):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

print("=" * 50)
print("首次部署到服务器")
print("=" * 50)

run(f'ssh {SERVER} "mkdir -p {REMOTE_DIR}"')
run(f'scp -r "{PROJECT_DIR}/backend" "{PROJECT_DIR}/frontend" "{PROJECT_DIR}/scripts/server" {SERVER}:{REMOTE_DIR}/')
run(f'ssh {SERVER} "chmod +x {REMOTE_DIR}/server/*.sh"')
run(f'ssh {SERVER} "cd {REMOTE_DIR} && ./server/install.sh"')
run(f'ssh {SERVER} "cd {REMOTE_DIR} && ./server/start.sh"')

print("=" * 50)
print(f"部署完成！访问: http://{SERVER_IP}:{SERVER_PORT}")
print("=" * 50)
