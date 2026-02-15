from unittest import result
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import ChatSession, ChatMessage, User
from auth.security import get_current_user
from backend.graph.graph import build_graph
from backend.graph.state import GraphState
from langchain_core.messages import HumanMessage, AIMessage

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
    .order_by(ChatMessage.created_at.desc())
    .limit(16)  # last 8 exchanges
)

    messages = list(reversed(result.scalars().all()))

    lc_messages = []

    for msg in messages:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_messages.append(AIMessage(content=msg.content))
    
    lc_messages.append(HumanMessage(content=content))
    
    state: GraphState = {
        "messages": lc_messages
    }

    final_state = await graph.ainvoke(state)

    last_message = final_state["messages"][-1]

    assistant_reply = last_message.content
    
    print("\n================= FINAL STATE =================")
    print("FINAL STATE:", final_state)
    print("=============================================\n")

    # store assistant reply
    db.add(ChatMessage(
    session_id=session_id,
    role="assistant",
    content=assistant_reply,
    ))
    await db.commit()

    return {"response": assistant_reply}