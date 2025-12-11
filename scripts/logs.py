"""查看日志"""
import subprocess
from config import SERVER, REMOTE_DIR

subprocess.run(f'ssh {SERVER} "tail -f {REMOTE_DIR}/server.log"', shell=True)
