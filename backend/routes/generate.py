"""
视频生成路由
"""
import os
import requests
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session as DBSession

from database import get_db
from models import Session, Message, MessageRole, MessageContentType, TaskStatus
from schemas import (
    TextToVideoRequest, 
    ImageToVideoRequest, 
    GenerateResponse, 
    TaskStatusResponse
)
from services.provider_factory import get_provider
from services.base_provider import TaskState
from config import SERVER_CONFIG, POLL_CONFIG
import time

router = APIRouter(prefix="/api/generate", tags=["generate"])


def poll_and_update_task(message_id: int, task_id: str):
    """后台轮询任务状态并更新数据库"""
    from database import SessionLocal
    
    provider = get_provider()
    db = SessionLocal()
    
    try:
        for _ in range(POLL_CONFIG["max_attempts"]):
            time.sleep(POLL_CONFIG["interval_seconds"])
            
            result = provider.query_task(task_id)
            message = db.query(Message).filter(Message.id == message_id).first()
            
            if not message:
                break
            
            if result.state == TaskState.SUCCESS:
                message.status = TaskStatus.SUCCESS
                message.video_url = result.video_url
                
                # 下载视频到本地
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
                        print(f"下载视频失败: {e}")
                
                db.commit()
                break
                
            elif result.state == TaskState.FAILED:
                message.status = TaskStatus.FAILED
                message.error_message = result.error_message
                db.commit()
                break
                
            elif result.state == TaskState.PROCESSING:
                message.status = TaskStatus.PROCESSING
                db.commit()
                
            # QUEUED状态继续轮询
            
    except Exception as e:
        message = db.query(Message).filter(Message.id == message_id).first()
        if message:
            message.status = TaskStatus.FAILED
            message.error_message = str(e)
            db.commit()
    finally:
        db.close()


@router.post("/text-to-video", response_model=GenerateResponse)
def text_to_video(
    data: TextToVideoRequest,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db)
):
    """文生视频"""
    # 验证会话存在
    session = db.query(Session).filter(Session.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 更新会话标题（使用prompt前20字符）
    if session.title == "新会话":
        session.title = data.prompt[:20] + ("..." if len(data.prompt) > 20 else "")
    
    # 创建用户消息
    user_message = Message(
        session_id=data.session_id,
        role=MessageRole.USER,
        content_type=MessageContentType.TEXT,
        content=data.prompt,
    )
    db.add(user_message)
    db.flush()
    
    # 创建AI响应消息（视频）
    ai_message = Message(
        session_id=data.session_id,
        role=MessageRole.ASSISTANT,
        content_type=MessageContentType.VIDEO,
        prompt=data.prompt,
        aspect_ratio=data.aspect_ratio,
        duration=data.duration,
        status=TaskStatus.PENDING,
    )
    db.add(ai_message)
    db.flush()
    
    # 提交生成任务
    try:
        provider = get_provider()
        task_id = provider.submit_task(
            prompt=data.prompt,
            aspect_ratio=data.aspect_ratio,
            duration=data.duration,
        )
        ai_message.task_id = task_id
        ai_message.status = TaskStatus.QUEUED
        db.commit()
        
        # 启动后台轮询
        background_tasks.add_task(poll_and_update_task, ai_message.id, task_id)
        
        return GenerateResponse(
            message_id=ai_message.id,
            task_id=task_id,
            status=TaskStatus.QUEUED,
        )
        
    except Exception as e:
        ai_message.status = TaskStatus.FAILED
        ai_message.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-to-video", response_model=GenerateResponse)
def image_to_video(
    data: ImageToVideoRequest,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db)
):
    """图生视频"""
    # 验证会话存在
    session = db.query(Session).filter(Session.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 更新会话标题
    if session.title == "新会话":
        session.title = data.prompt[:20] + ("..." if len(data.prompt) > 20 else "")
    
    # 创建用户消息（包含图片和文本）
    user_message = Message(
        session_id=data.session_id,
        role=MessageRole.USER,
        content_type=MessageContentType.IMAGE,
        content=data.prompt,
        reference_image=data.image_url,
    )
    db.add(user_message)
    db.flush()
    
    # 创建AI响应消息（视频）
    ai_message = Message(
        session_id=data.session_id,
        role=MessageRole.ASSISTANT,
        content_type=MessageContentType.VIDEO,
        prompt=data.prompt,
        reference_image=data.image_url,
        aspect_ratio=data.aspect_ratio,
        duration=data.duration,
        status=TaskStatus.PENDING,
    )
    db.add(ai_message)
    db.flush()
    
    # 提交生成任务
    try:
        provider = get_provider()
        task_id = provider.submit_task(
            prompt=data.prompt,
            image_url=data.image_url,
            aspect_ratio=data.aspect_ratio,
            duration=data.duration,
        )
        ai_message.task_id = task_id
        ai_message.status = TaskStatus.QUEUED
        db.commit()
        
        # 启动后台轮询
        background_tasks.add_task(poll_and_update_task, ai_message.id, task_id)
        
        return GenerateResponse(
            message_id=ai_message.id,
            task_id=task_id,
            status=TaskStatus.QUEUED,
        )
        
    except Exception as e:
        ai_message.status = TaskStatus.FAILED
        ai_message.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{message_id}", response_model=TaskStatusResponse)
def get_task_status(message_id: int, db: DBSession = Depends(get_db)):
    """查询消息/任务状态"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    return TaskStatusResponse(
        message_id=message.id,
        status=message.status,
        video_url=message.video_url,
        error_message=message.error_message,
    )


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """上传图片（用于图生视频）- 同时上传到图床获取公网URL"""
    import uuid
    print(f"[上传图片] 收到文件: {file.filename}")
    
    uploads_dir = SERVER_CONFIG["uploads_dir"]
    os.makedirs(uploads_dir, exist_ok=True)
    
    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(uploads_dir, filename)
    
    # 读取文件内容
    content = await file.read()
    
    # 保存到本地（用于预览）
    with open(filepath, "wb") as f:
        f.write(content)
    print(f"[上传图片] 已保存到本地: {filepath}")
    
    # 上传到GitHub图床获取公网URL
    public_url = None
    import base64
    
    # GitHub 图床配置（从 credentials.py 读取）
    try:
        from credentials import GITHUB_TOKEN, GITHUB_REPO
    except ImportError:
        GITHUB_TOKEN = ""
        GITHUB_REPO = "hezawei/image-bed"
    
    if GITHUB_TOKEN:
        try:
            img_base64 = base64.b64encode(content).decode('utf-8')
            github_api = f"https://api.github.com/repos/{GITHUB_REPO}/contents/images/{filename}"
            
            response = requests.put(
                github_api,
                headers={
                    "Authorization": f"token {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "message": f"Upload {filename}",
                    "content": img_base64
                },
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                # 构造 raw 链接
                public_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/images/{filename}"
                print(f"GitHub上传成功: {public_url}")
            else:
                print(f"GitHub上传失败: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"GitHub上传失败: {e}")
    else:
        print("[警告] 未配置 GITHUB_TOKEN，图生视频功能不可用")
        print("请创建 GitHub Token: https://github.com/settings/tokens")
    
    # 返回本地预览URL和公网URL
    return {
        "filename": filename, 
        "url": f"/uploads/{filename}",  # 本地预览用
        "public_url": public_url  # 传给API用
    }


@router.get("/extract-frame")
async def extract_last_frame(video_url: str):
    """提取视频最后一帧，返回 base64 图片"""
    import cv2
    import numpy as np
    import base64
    import tempfile
    
    print(f"[提取尾帧] URL: {video_url}")
    
    try:
        # 下载视频到临时文件
        response = requests.get(video_url, timeout=30)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        # 用 OpenCV 读取视频
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="无法打开视频")
        
        # 跳转到最后一帧
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, total_frames - 1))
        
        ret, frame = cap.read()
        cap.release()
        
        # 删除临时文件
        os.unlink(tmp_path)
        
        if not ret:
            raise HTTPException(status_code=500, detail="无法读取帧")
        
        # 转换为 PNG 并编码为 base64
        _, buffer = cv2.imencode('.png', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        print(f"[提取尾帧] 成功，图片大小: {len(img_base64)} 字符")
        
        return {"image": f"data:image/png;base64,{img_base64}"}
        
    except requests.RequestException as e:
        print(f"[提取尾帧] 下载失败: {e}")
        raise HTTPException(status_code=500, detail=f"下载视频失败: {e}")
    except Exception as e:
        print(f"[提取尾帧] 处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理失败: {e}")
