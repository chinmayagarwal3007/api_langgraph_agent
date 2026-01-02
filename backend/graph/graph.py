from langgraph.graph import StateGraph, END
from backend.graph.state import GraphState
from backend.llm.gemini import generate
from backend.prompts.intent_prompt import INTENT_PROMPT
from backend.prompts.respond_prompt import RESPOND_PROMPT


async def detect_intent(state: GraphState) -> GraphState:
    chat = "\n".join(
        f"{m['role']}: {m['content']}" for m in state["chat_history"]
    )

    prompt = INTENT_PROMPT.format(
        chat_history=chat,
        user_input=state["user_input"],
    )

    intent = (await generate(prompt)).strip()
    state["intent"] = intent
    return state


async def respond(state: GraphState) -> GraphState:
    chat = "\n".join(
        f"{m['role']}: {m['content']}" for m in state["chat_history"]
    )

    prompt = RESPOND_PROMPT.format(
        chat_history=chat,
        user_input=state["user_input"],
    )

    state["response"] = await generate(prompt)
    return state


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("intent", detect_intent)
    graph.add_node("respond", respond)

    graph.set_entry_point("intent")
    graph.add_edge("intent", "respond")
    graph.add_edge("respond", END)

    return graph.compile()
