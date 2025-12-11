"""SSH连接服务器"""
import subprocess
from config import SERVER

subprocess.run(f'ssh {SERVER}', shell=True)
