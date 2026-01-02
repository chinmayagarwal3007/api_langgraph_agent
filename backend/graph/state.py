from typing import TypedDict, List, Optional, Dict, Any


class Message(TypedDict):
    role: str
    content: str


class GraphState(TypedDict):
    user_id: int
    session_id: int

    chat_history: List[Message]
    user_input: str

    intent: Optional[str]
    response: Optional[str]
