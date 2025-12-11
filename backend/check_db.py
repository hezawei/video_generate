from database import SessionLocal
from models import Message

db = SessionLocal()
messages = db.query(Message).order_by(Message.id.desc()).limit(5).all()

print("ID | Role | Status | Task ID | Content")
print("-" * 50)
for msg in messages:
    content = msg.content[:20] if msg.content else "VIDEO"
    print(f"{msg.id} | {msg.role} | {msg.status} | {msg.task_id} | {content}")
