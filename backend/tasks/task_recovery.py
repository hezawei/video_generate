"""
任务恢复模块
服务启动时自动恢复未完成的轮询任务
"""
import threading
import time
from database import SessionLocal
from models import Message, TaskStatus
from services.provider_factory import get_provider
from services.base_provider import TaskState
from config import POLL_CONFIG, SERVER_CONFIG
import requests
import os


def poll_single_task(message_id: int, task_id: str):
    """轮询单个任务"""
    provider = get_provider()
    db = SessionLocal()
    
    try:
        for _ in range(POLL_CONFIG["max_attempts"]):
            time.sleep(POLL_CONFIG["interval_seconds"])
            
            try:
                result = provider.query_task(task_id)
            except Exception as e:
                print(f"[Recovery] 查询任务 {task_id} 失败: {e}")
                continue
            
            message = db.query(Message).filter(Message.id == message_id).first()
            if not message:
                print(f"[Recovery] 消息 {message_id} 不存在，停止轮询")
                break
            
            if result.state == TaskState.SUCCESS:
                message.status = TaskStatus.SUCCESS
                message.video_url = result.video_url
                
                # 下载视频
                if result.video_url:
                    try:
                        downloads_dir = SERVER_CONFIG["downloads_dir"]
                        os.makedirs(downloads_dir, exist_ok=True)
                        video_filename = f"{task_id}.mp4"
                        local_path = os.path.join(downloads_dir, video_filename)
                        
                        response = requests.get(result.video_url, timeout=120)
                        response.raise_for_status()
                        with open(local_path, "wb") as f:
                            f.write(response.content)
                        message.local_path = video_filename
                    except Exception as e:
                        print(f"[Recovery] 下载视频失败: {e}")
                
                db.commit()
                print(f"[Recovery] 任务 {task_id} 完成")
                break
                
            elif result.state == TaskState.FAILED:
                message.status = TaskStatus.FAILED
                message.error_message = result.error_message
                db.commit()
                print(f"[Recovery] 任务 {task_id} 失败: {result.error_message}")
                break
                
            elif result.state == TaskState.PROCESSING:
                if message.status != TaskStatus.PROCESSING:
                    message.status = TaskStatus.PROCESSING
                    db.commit()
                    
    except Exception as e:
        print(f"[Recovery] 轮询任务 {task_id} 出错: {e}")
        message = db.query(Message).filter(Message.id == message_id).first()
        if message:
            message.status = TaskStatus.FAILED
            message.error_message = f"轮询出错: {str(e)}"
            db.commit()
    finally:
        db.close()


def start_recovery_daemon():
    """启动任务恢复守护线程"""
    def daemon_loop():
        while True:
            try:
                recover_pending_tasks()
            except Exception as e:
                print(f"[Daemon] 守护线程出错: {e}")
            # 每60秒检查一次
            time.sleep(60)

    thread = threading.Thread(target=daemon_loop, daemon=True)
    thread.start()
    print("[Daemon] 任务恢复守护线程已启动")


def recover_pending_tasks():
    """恢复所有未完成的任务"""
    db = SessionLocal()
    try:
        # 查找所有未完成的任务
        pending_messages = db.query(Message).filter(
            Message.task_id.isnot(None),
            Message.status.in_([
                TaskStatus.PENDING,
                TaskStatus.QUEUED,
                TaskStatus.PROCESSING
            ])
        ).all()
        
        if not pending_messages:
            # print("[Recovery] 没有需要恢复的任务") # 减少日志噪音
            return
            
        for msg in pending_messages:
            # 检查该任务是否已经在运行轮询（避免重复启动）
            # 这里简单起见，只要有未完成的就尝试查询一次
            # 实际生产中可以使用缓存或锁来标记正在轮询的任务
            # 但由于BaseProvider的query操作是幂等的，多查询几次问题不大
            
            # 使用一次性线程查询状态，而不是启动长轮询，
            # 因为守护线程本身就是周期性的。
            thread = threading.Thread(
                target=poll_single_task_once,
                args=(msg.id, msg.task_id),
                daemon=True
            )
            thread.start()
            
    finally:
        db.close()

def poll_single_task_once(message_id: int, task_id: str):
    """执行单次查询更新（由守护线程调用）"""
    provider = get_provider()
    db = SessionLocal()
    try:
        result = provider.query_task(task_id)
        
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message: return

        # 只有状态发生变化或需要更新时才写入
        if result.state == TaskState.SUCCESS and message.status != TaskStatus.SUCCESS:
            print(f"[Recovery] 任务 {task_id} 变更为成功")
            message.status = TaskStatus.SUCCESS
            message.video_url = result.video_url
            # 下载视频逻辑...
            if result.video_url:
                try:
                    downloads_dir = SERVER_CONFIG["downloads_dir"]
                    os.makedirs(downloads_dir, exist_ok=True)
                    video_filename = f"{task_id}.mp4"
                    local_path = os.path.join(downloads_dir, video_filename)
                    if not os.path.exists(local_path): # 避免重复下载
                        response = requests.get(result.video_url, timeout=120)
                        response.raise_for_status()
                        with open(local_path, "wb") as f:
                            f.write(response.content)
                        message.local_path = video_filename
                except Exception as e:
                    print(f"[Recovery] 下载视频失败: {e}")
            db.commit()
            
        elif result.state == TaskState.FAILED and message.status != TaskStatus.FAILED:
            print(f"[Recovery] 任务 {task_id} 变更为失败")
            message.status = TaskStatus.FAILED
            message.error_message = result.error_message
            db.commit()
            
        elif result.state == TaskState.PROCESSING and message.status != TaskStatus.PROCESSING:
             message.status = TaskStatus.PROCESSING
             db.commit()
             
    except Exception as e:
        print(f"[Recovery] 查询任务 {task_id} 出错: {e}")
    finally:
        db.close()

