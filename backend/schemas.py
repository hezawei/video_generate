"""
Pydantic schemas for API request/response
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# Session schemas
class SessionCreate(BaseModel):
    title: Optional[str] = "新会话"


class SessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Message schemas
class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content_type: str
    content: Optional[str]
    task_id: Optional[str]
    status: str
    video_url: Optional[str]
    local_path: Optional[str]
    error_message: Optional[str]
    prompt: Optional[str]
    reference_image: Optional[str]
    aspect_ratio: str
    duration: str
    created_at: datetime

    class Config:
        from_attributes = True


# Generate request schemas
class TextToVideoRequest(BaseModel):
    session_id: int
    prompt: str
    aspect_ratio: str = "9:16"
    duration: str = "10"


class ImageToVideoRequest(BaseModel):
    session_id: int
    prompt: str
    image_url: str  # 参考图片URL
    aspect_ratio: str = "9:16"
    duration: str = "10"


class GenerateResponse(BaseModel):
    message_id: int
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    message_id: int
    status: str
    video_url: Optional[str]
    error_message: Optional[str]
