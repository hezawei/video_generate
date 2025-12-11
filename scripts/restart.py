"""重启服务"""
import subprocess
from config import SERVER, REMOTE_DIR

def run(cmd):
    print(f">>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)

run(f'ssh {SERVER} "cd {REMOTE_DIR} && ./server/stop.sh && ./server/start.sh"')
print("服务已重启")
