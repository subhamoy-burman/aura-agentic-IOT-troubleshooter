# Agent State Management
# This file contains the state management logic for the Aura agent

from typing import TypedDict, Annotated
from operator import add
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    State object for the Aura IoT troubleshooter agent.
    
    The state tracks:
    - chat_history: Conversation including user messages, AI responses, and tool results
      The 'add' reducer ensures messages are appended, not replaced
    - user_id: Identifies which user this conversation belongs to
    - session_id: Identifies which session within a user's history
    
    This state is passed between nodes in the LangGraph workflow and enables:
    1. Multi-turn reasoning loops (agent can call multiple tools)
    2. Persistent memory (load/save from database)
    3. User-specific context tracking
    """
    # The 'add' reducer tells LangGraph to append new messages to the list
    # Without this, returning {"chat_history": [new_msg]} would REPLACE the entire list
    # With this, it APPENDS to the existing list
    chat_history: Annotated[list[BaseMessage], add]
    
    # User identification for memory persistence
    user_id: str
    
    # Session identification for grouping conversations
    session_id: str