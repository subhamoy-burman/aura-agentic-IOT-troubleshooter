# Agent State Management
# This file will contain the state management logic for the Aura agent

from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    State object for the Aura IoT troubleshooter agent.
    
    The state tracks the conversation history which includes:
    - User messages (HumanMessage)
    - Agent responses (AIMessage) 
    - Tool execution results (ToolMessage)
    
    This state is passed between nodes in the LangGraph workflow.
    """
    chat_history: List[BaseMessage]