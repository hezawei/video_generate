"""本地开发启动脚本 - 自动清理旧进程"""
import subprocess
import sys
import os
import signal

def kill_port(port):
    """杀掉占用指定端口的进程"""
    try:
        # Windows
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}"',
            shell=True, capture_output=True, text=True
        )
        for line in result.stdout.strip().split('\n'):
            if 'LISTENING' in line:
                parts = line.split()
                pid = parts[-1]
                if pid.isdigit():
                    print(f"[清理] 杀掉占用端口 {port} 的进程 PID={pid}")
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, 
                                 capture_output=True)
    except Exception as e:
        print(f"[警告] 清理端口失败: {e}")

def main():
    port = 8002
    
    # 先清理旧进程
    print(f"[启动] 检查并清理端口 {port}...")
    kill_port(port)
    
    # 启动 uvicorn
    print(f"[启动] 启动后端服务 http://127.0.0.1:{port}")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app", "--reload", "--port", str(port)
        ])
    except KeyboardInterrupt:
        print("\n[停止] 正在关闭...")
        # 再次清理，确保没有残留
        kill_port(port)
        print("[停止] 已关闭")

if __name__ == "__main__":
    main()
