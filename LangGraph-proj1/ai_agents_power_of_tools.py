from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
import requests

from dotenv import load_dotenv

# Load environment variables (e.g. OPENAI_API_KEY)
load_dotenv()

# Set up your LLM - the brain of your agent
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Custom Web Search Tool
class WebSearchTool:
    name = "web_search"

    def invoke(self, args: dict) -> str:
        """Perform a DuckDuckGo Instant Answer search and return the abstract."""
        query = args.get("query", "")
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1}
        )
        data = resp.json()
        # If DuckDuckGo returns an abstract, use it; otherwise list related topics
        if text := data.get("AbstractText"):
            return text
        # fall back to RelatedTopics titles
        topics = data.get("RelatedTopics", [])
        titles = [t.get("Text") for t in topics if t.get("Text")]
        return "\n".join(titles[:5]) or "No results found."


# Step 2: Define the Agent's Memory and Tools
class State(TypedDict):
    messages: Annotated[list, add_messages]


def get_tools():
    """Your agent's capabilities."""
    return [
        TavilySearchResults(max_results=3, search_depth="advanced")
    ]


# Step 3: The Thinking Node

def llm_node(state: State):
    """Your agent's brain: decides whether to call tools or respond directly."""
    tools = get_tools()
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


#  Step 4: The Action Node

def tools_node(state: State):
    """Your agent's hands: executes the tools it requested."""
    tools = get_tools()
    tool_registry = {tool.name: tool for tool in tools}

    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in last_message.tool_calls:
        tool = tool_registry[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            )
        )

    return {"messages": tool_messages}


#  Step 5: The Decision Logic

def should_continue(state: State):
    """Decides whether to call tools again or finish."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# Step 6: Building the Complete Workflow

def create_agent():
    graph = StateGraph(State)

    graph.add_node("llm", llm_node)
    graph.add_node("tools", tools_node)
    graph.set_entry_point("llm")

    graph.add_conditional_edges(
        "llm",
        should_continue,
        {"tools": "tools", END: END}
    )
    graph.add_edge("tools", "llm")

    return graph.compile()


# Step 7: Testing Your Enhanced Agent

def main():
    agent = create_agent()

    initial_state = {
        "messages": [
            SystemMessage(
                content=(
                    "You are a helpful assistant with access to web search. "
                    "Use the search tool when you need current information."
                )
            ),
            HumanMessage(
                content="What's the latest news about AI developments in 2025?"
            )
        ]
    }

    result = agent.invoke(initial_state)
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
