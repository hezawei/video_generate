"""
图片生成路由
"""
import os
import uuid
import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import Session, Message, MessageRole, MessageContentType, TaskStatus
from config import SERVER_CONFIG
from services.gemini_image_provider import get_image_provider

router = APIRouter(prefix="/api/image", tags=["图片生成"])


class TextToImageRequest(BaseModel):
    """文生图请求"""
    session_id: int
    prompt: str


class ImageToImageRequest(BaseModel):
    """图生图请求"""
    session_id: int
    prompt: str
    reference_image: str  # base64 或 URL


class ImageGenerateResponse(BaseModel):
    """图片生成响应"""
    message_id: int
    image_url: str


@router.post("/text-to-image", response_model=ImageGenerateResponse)
async def text_to_image(request: TextToImageRequest, db: DBSession = Depends(get_db)):
    """文生图"""
    print(f"[文生图] session={request.session_id}, prompt={request.prompt[:30]}...")
    
    # 检查会话
    session = db.query(Session).filter(Session.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 创建用户消息
    user_message = Message(
        session_id=request.session_id,
        role=MessageRole.USER,
        content_type=MessageContentType.TEXT,
        content=request.prompt,
        status=TaskStatus.SUCCESS,
    )
    db.add(user_message)
    db.commit()
    
    # 调用图片生成服务
    try:
        provider = get_image_provider()
        result = provider.generate_image(prompt=request.prompt)
        
        # 保存图片到本地
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(SERVER_CONFIG["downloads_dir"], filename)
        os.makedirs(SERVER_CONFIG["downloads_dir"], exist_ok=True)
        
        img_bytes = base64.b64decode(result["image_base64"])
        with open(filepath, "wb") as f:
            f.write(img_bytes)
        
        image_url = f"/downloads/{filename}"
        
        # 创建AI响应消息
        ai_message = Message(
            session_id=request.session_id,
            role=MessageRole.ASSISTANT,
            content_type=MessageContentType.IMAGE,
            content=result.get("content", ""),
            prompt=request.prompt,
            status=TaskStatus.SUCCESS,
            video_url=image_url,  # 复用 video_url 字段存储图片URL
            local_path=filepath,
        )
        db.add(ai_message)
        db.commit()
        
        # 更新会话标题
        if session.title == "新会话":
            session.title = request.prompt[:20] + "..." if len(request.prompt) > 20 else request.prompt
            db.commit()
        
        print(f"[文生图] 成功，image_url={image_url}")
        return ImageGenerateResponse(message_id=ai_message.id, image_url=image_url)
        
    except Exception as e:
        print(f"[文生图] 失败: {e}")
        # 创建失败消息
        ai_message = Message(
            session_id=request.session_id,
            role=MessageRole.ASSISTANT,
            content_type=MessageContentType.IMAGE,
            prompt=request.prompt,
            status=TaskStatus.FAILED,
            error_message=str(e),
        )
        db.add(ai_message)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-to-image", response_model=ImageGenerateResponse)
async def image_to_image(request: ImageToImageRequest, db: DBSession = Depends(get_db)):
    """图生图"""
    print(f"[图生图] session={request.session_id}, prompt={request.prompt[:30]}...")
    
    # 检查会话
    session = db.query(Session).filter(Session.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 处理参考图片
    reference_image_base64 = request.reference_image
    if request.reference_image.startswith("http") or request.reference_image.startswith("/"):
        # URL 形式，需要下载并转换
        import requests
        if request.reference_image.startswith("/"):
            # 本地路径
            local_path = os.path.join(os.path.dirname(SERVER_CONFIG["uploads_dir"]), request.reference_image.lstrip("/"))
            with open(local_path, "rb") as f:
                reference_image_base64 = base64.b64encode(f.read()).decode()
        else:
            # 远程URL
            resp = requests.get(request.reference_image, timeout=30)
            reference_image_base64 = base64.b64encode(resp.content).decode()
    elif request.reference_image.startswith("data:"):
        # data URL 形式
        reference_image_base64 = request.reference_image.split(",")[1]
    
    # 创建用户消息
    user_message = Message(
        session_id=request.session_id,
        role=MessageRole.USER,
        content_type=MessageContentType.IMAGE,
        content=request.prompt,
        reference_image=request.reference_image[:200],  # 截断存储
        status=TaskStatus.SUCCESS,
    )
    db.add(user_message)
    db.commit()
    
    # 调用图片生成服务
    try:
        provider = get_image_provider()
        result = provider.generate_image(
            prompt=request.prompt,
            reference_image_base64=reference_image_base64,
        )
        
        # 保存图片到本地
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(SERVER_CONFIG["downloads_dir"], filename)
        os.makedirs(SERVER_CONFIG["downloads_dir"], exist_ok=True)
        
        img_bytes = base64.b64decode(result["image_base64"])
        with open(filepath, "wb") as f:
            f.write(img_bytes)
        
        image_url = f"/downloads/{filename}"
        
        # 创建AI响应消息
        ai_message = Message(
            session_id=request.session_id,
            role=MessageRole.ASSISTANT,
            content_type=MessageContentType.IMAGE,
            content=result.get("content", ""),
            prompt=request.prompt,
            status=TaskStatus.SUCCESS,
            video_url=image_url,
            local_path=filepath,
        )
        db.add(ai_message)
        db.commit()
        
        # 更新会话标题
        if session.title == "新会话":
            session.title = request.prompt[:20] + "..." if len(request.prompt) > 20 else request.prompt
            db.commit()
        
        print(f"[图生图] 成功，image_url={image_url}")
        return ImageGenerateResponse(message_id=ai_message.id, image_url=image_url)
        
    except Exception as e:
        print(f"[图生图] 失败: {e}")
        ai_message = Message(
            session_id=request.session_id,
            role=MessageRole.ASSISTANT,
            content_type=MessageContentType.IMAGE,
            prompt=request.prompt,
            status=TaskStatus.FAILED,
            error_message=str(e),
        )
        db.add(ai_message)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
