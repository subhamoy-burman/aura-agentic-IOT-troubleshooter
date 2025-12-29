# LangGraph State Graph for Aura Agent
# This file contains the main graph logic for the agent workflow

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage
from typing import Dict, Any, Literal
import os
from dotenv import load_dotenv

# Load environment variables (critical for Azure OpenAI credentials)
load_dotenv()

from .agent_state import AgentState
# Import all your tools
from .tools import check_device_connectivity, get_device_error_logs, search_troubleshooting_guides

# System prompt that guides the LLM's decision-making
SYSTEM_PROMPT = """You are Aura, an expert IoT troubleshooting assistant. Your goal is to help users diagnose and resolve issues with their IoT devices.

When a user reports a problem:
1. First, use search_troubleshooting_guides to find relevant documentation for error codes or symptoms
2. If needed, use check_device_connectivity to verify the device's network status
3. If needed, use get_device_error_logs to review recent device logs
4. After gathering sufficient information, provide a clear, step-by-step troubleshooting guide

Be concise, helpful, and prioritize the most likely solutions first. Always explain technical terms in simple language."""

# Initialize tools and the main LLM
tools = [check_device_connectivity, get_device_error_logs, search_troubleshooting_guides]
tool_node = ToolNode(tools)

llm = AzureChatOpenAI(
    azure_deployment=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    api_version=os.environ.get("OPENAI_API_VERSION", "2024-02-15-preview"),
    temperature=0).bind_tools(tools)

def call_model(state: AgentState) -> dict:
    """
    The primary node for the agent's reasoning loop.
    
    THIS IS WHERE THE LLM DECIDES TO CALL TOOLS:
    - The LLM receives the chat history (including system prompt)
    - It analyzes the user's query: "My vacuum cleaner shows error E-401"
    - It sees it has tools like search_troubleshooting_guides
    - It autonomously decides: "I should call search_troubleshooting_guides with query='E-401'"
    - Returns an AIMessage with tool_calls=[{name: 'search_troubleshooting_guides', args: {...}}]
    """
    print(f"---CALLING LLM for user: {state.get('user_id', 'unknown')}---")
    messages = state["chat_history"]
    
    # Ensure system prompt is always at the start of the conversation
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    response = llm.invoke(messages)
    # The response is an AIMessage that can contain tool_calls
    # Thanks to the 'add' reducer in AgentState, this will APPEND to chat_history
    return {"chat_history": [response]}

# Define the conditional edge
def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """The router that decides what to do next."""
    last_message = state["chat_history"][-1]
    if last_message.tool_calls:
        # If the LLM requested to call a tool, we route to the tool node
        return "tools"
    # Otherwise, we are done
    return "end"

def create_aura_graph() -> StateGraph:
    """
    Create and return the main Aura agent graph.
    
    Graph Flow:
    1. User query enters the graph
    2. call_model node: LLM reasons about the query and decides next action
    3. should_continue router: Checks if LLM wants to use tools
       - If tool_calls exist → route to "tools" node
       - If no tool_calls → route to "end" (done)
    4. tools node: Executes requested tools and adds results to chat history
    5. Loop back to call_model to process tool results
    6. Continue until LLM is satisfied and provides final answer
    
    Returns:
        Compiled StateGraph ready to invoke
    """
    
    # Initialize the state graph with our AgentState schema
    graph = StateGraph(AgentState)
    
    # Add nodes to the graph
    # Node 1: The agent's reasoning loop (calls the LLM)
    graph.add_node("agent", call_model)
    
    # Node 2: Tool execution node (runs the tools requested by LLM)
    graph.add_node("tools", tool_node)
    
    # Set the entry point - where the graph starts
    graph.set_entry_point("agent")
    
    # Add conditional edge from agent node
    # After the agent reasons, we check if it wants to use tools
    graph.add_conditional_edges(
        "agent",  # Source node
        should_continue,  # Decision function
        {
            "tools": "tools",  # If should_continue returns "tools", go to tools node
            "end": END  # If should_continue returns "end", finish the graph
        }
    )
    
    # Add edge from tools back to agent
    # After tools execute, always go back to the agent to process results
    graph.add_edge("tools", "agent")
    
    # Compile the graph into a runnable
    return graph.compile()


# For easy import
aura_graph = create_aura_graph()