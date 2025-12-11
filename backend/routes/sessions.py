"""
会话管理路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from database import get_db
from models import Session, Message
from schemas import SessionCreate, SessionResponse, MessageResponse

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=List[SessionResponse])
def get_sessions(db: DBSession = Depends(get_db)):
    """获取所有会话列表"""
    sessions = db.query(Session).order_by(Session.updated_at.desc()).all()
    return sessions


@router.post("", response_model=SessionResponse)
def create_session(data: SessionCreate, db: DBSession = Depends(get_db)):
    """创建新会话"""
    session = Session(title=data.title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: DBSession = Depends(get_db)):
    """获取单个会话"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(session_id: int, data: SessionCreate, db: DBSession = Depends(get_db)):
    """更新会话标题"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    session.title = data.title
    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}")
def delete_session(session_id: int, db: DBSession = Depends(get_db)):
    """删除会话"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.delete(session)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages(session_id: int, db: DBSession = Depends(get_db)):
    """获取会话的所有消息"""
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
    return messages
