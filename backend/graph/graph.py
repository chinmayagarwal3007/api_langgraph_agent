from langgraph.graph import StateGraph, END
from backend.graph.state import GraphState
from backend.llm.gemini import llm
from backend.prompts.intent_prompt import INTENT_PROMPT
from backend.prompts.respond_prompt import RESPOND_PROMPT
from langchain_core.messages import HumanMessage, SystemMessage
from ..tools.api_executor import execute_api
from langgraph.prebuilt import ToolNode

useful_tools = [execute_api]

llm = llm.bind_tools(useful_tools)


async def detect_intent(state: GraphState):
    messages = [
        SystemMessage(content=INTENT_PROMPT),
        *state["messages"], # existing conversation
    ]

    response = await llm.ainvoke(messages)

    print("\n==================================================\n") 
    print("LLM Response:", response)
    print("====================================================\n")

    if response.tool_calls:
        print("Tool decision:", response.tool_calls[0]["name"])
    else:
        print("No tool called. Normal LLM response.")
    
    return {
    "messages": [response]
    }

tool_node = ToolNode(useful_tools)

async def respond(state: GraphState) -> GraphState:
     print("\n===== STATE MESSAGES =====")
     for m in state["messages"]:
         print(type(m), getattr(m, "content", None))
     print("==========================\n")     


     messages = [
        SystemMessage(content=RESPOND_PROMPT),
        *state["messages"],
    ]
     
     response = await llm.ainvoke(messages)

     return {
    "messages": [response]
    }


def route_after_intent(state: GraphState):

    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "respond"



def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("intent", detect_intent)
    graph.add_node("respond", respond)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("intent")

    graph.add_conditional_edges(
        "intent",
        route_after_intent,
        {
            "tools": "tools",
            "respond": "respond",
        },
    )

    graph.add_edge("tools", "respond")
    graph.add_edge("respond", END)

    return graph.compile()
