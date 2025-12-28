from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from db.models import ChatSession, ChatMessage, User
from auth.security import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions")
async def create_session(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = ChatSession(user_id=user.id)
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {"session_id": session.id}


@router.get("/sessions")
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession).where(ChatSession.user_id == user.id)
    )
    sessions = result.scalars().all()

    return [
        {"id": s.id, "created_at": s.created_at}
        for s in sessions
    ]


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: int,
    content: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=content,
    )
    db.add(msg)
    await db.commit()

    return {"status": "message stored"}
