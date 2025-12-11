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
    """上传图片（用于图生视频）"""
    uploads_dir = SERVER_CONFIG["uploads_dir"]
    os.makedirs(uploads_dir, exist_ok=True)
    
    # 生成唯一文件名
    import uuid
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(uploads_dir, filename)
    
    # 保存文件
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    
    # 返回可访问的URL
    return {"filename": filename, "url": f"/uploads/{filename}"}
