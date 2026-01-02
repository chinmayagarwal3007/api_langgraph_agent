from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import ChatSession, ChatMessage, User
from auth.security import get_current_user
from backend.graph.graph import build_graph
from backend.graph.state import GraphState

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


graph = build_graph()


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: int,
    content: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # store user message
    db.add(ChatMessage(
        session_id=session_id,
        role="user",
        content=content,
    ))
    await db.commit()

    # load chat history
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()

    state: GraphState = {
        "user_id": user.id,
        "session_id": session_id,
        "chat_history": [
            {"role": m.role, "content": m.content} for m in messages
        ],
        "user_input": content,
        "intent": None,
        "response": None,
    }

    final_state = await graph.ainvoke(state)

    # store assistant reply
    db.add(ChatMessage(
        session_id=session_id,
        role="assistant",
        content=final_state["response"],
    ))
    await db.commit()

    return {"response": final_state["response"]}