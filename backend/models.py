"""
数据模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from database import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageContentType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"      # 等待提交
    QUEUED = "queued"        # 排队中
    PROCESSING = "processing"  # 生成中
    SUCCESS = "success"      # 成功
    FAILED = "failed"        # 失败


class Session(Base):
    """会话表"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="新会话")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20), default=MessageRole.USER)
    content_type = Column(String(20), default=MessageContentType.TEXT)
    content = Column(Text)  # 文本内容或图片路径
    
    # 视频生成相关
    task_id = Column(String(100), nullable=True)  # 中转商返回的任务ID
    status = Column(String(20), default=TaskStatus.PENDING)
    video_url = Column(Text, nullable=True)  # 远程视频URL
    local_path = Column(Text, nullable=True)  # 本地下载路径
    error_message = Column(Text, nullable=True)  # 错误信息
    
    # 生成参数
    prompt = Column(Text, nullable=True)
    reference_image = Column(Text, nullable=True)  # 参考图片URL
    aspect_ratio = Column(String(10), default="9:16")
    duration = Column(String(10), default="10")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")
