"""一键配置SSH免密登录"""
import subprocess
import os
from config import SERVER, SERVER_IP, SERVER_USER

SSH_DIR = os.path.expanduser("~/.ssh")
KEY_FILE = os.path.join(SSH_DIR, "id_rsa")
PUB_KEY_FILE = KEY_FILE + ".pub"

print("=" * 50)
print("配置SSH免密登录")
print("=" * 50)

# 1. 检查是否已有密钥
if not os.path.exists(PUB_KEY_FILE):
    print("\n[1/2] 生成SSH密钥...")
    os.makedirs(SSH_DIR, exist_ok=True)
    subprocess.run(f'ssh-keygen -t rsa -b 4096 -f "{KEY_FILE}" -N ""', shell=True, check=True)
else:
    print("\n[1/2] SSH密钥已存在，跳过生成")

# 2. 上传公钥到服务器
print("\n[2/2] 上传公钥到服务器（需要输入一次密码）...")
# 读取公钥
with open(PUB_KEY_FILE, "r") as f:
    pub_key = f.read().strip()

# 使用ssh-copy-id或手动追加
cmd = f'ssh {SERVER} "mkdir -p ~/.ssh && echo \'{pub_key}\' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"'
print(f">>> {cmd}")
subprocess.run(cmd, shell=True)

print("\n" + "=" * 50)
print("配置完成！以后SSH将自动免密登录")
print("测试: ssh " + SERVER)
print("=" * 50)
