"""
Aura IoT Troubleshooter - Streamlit Web Interface

A conversational AI agent for IoT device troubleshooting with:
- Long-term memory (PostgreSQL persistence)
- Multi-turn reasoning (LangGraph state machine)
- RAG-powered knowledge retrieval
- Session management and history browsing

Usage:
    streamlit run app.py
"""

import streamlit as st
import os
import sys
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the aura-agent directory to Python path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aura-agent'))

# Import the compiled LangGraph agent and memory manager
from src.graph import aura_graph
from src.memory_manager import ChatHistoryManager

# --- Page Configuration ---
st.set_page_config(
    page_title="Aura IoT Troubleshooter",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for better UI ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .sidebar-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Memory Manager ---
@st.cache_resource
def get_memory_manager():
    """Initialize the memory manager (cached to persist across reruns)."""
    return ChatHistoryManager(max_history_messages=20)

memory_manager = get_memory_manager()

# --- Session State Initialization ---
def initialize_session():
    """Initialize Streamlit session state variables."""
    
    # User identification (in production, this would come from auth)
    if "user_id" not in st.session_state:
        st.session_state.user_id = "default_user"
    
    # Session management
    if "session_id" not in st.session_state:
        # Start a new session
        st.session_state.session_id = memory_manager.start_new_session(
            st.session_state.user_id,
            title=f"Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
    
    # Load chat history from database
    if "messages" not in st.session_state:
        loaded_history = memory_manager.load_history(
            st.session_state.user_id,
            st.session_state.session_id
        )
        
        if loaded_history:
            st.session_state.messages = loaded_history
        else:
            # New conversation - start with greeting
            greeting = AIMessage(content="Hello! I'm Aura, your IoT troubleshooting assistant. How can I help you today?")
            st.session_state.messages = [greeting]
            # Save the greeting to database
            memory_manager.save_message(
                st.session_state.user_id,
                st.session_state.session_id,
                greeting
            )

initialize_session()

# --- Sidebar: Session Management ---
with st.sidebar:
    st.markdown("### 🗂️ Conversation Management")
    
    # New conversation button
    if st.button("➕ Start New Conversation", use_container_width=True):
        # Create a new session
        new_session_id = memory_manager.start_new_session(
            st.session_state.user_id,
            title=f"Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        st.session_state.session_id = new_session_id
        
        # Reset messages with greeting
        greeting = AIMessage(content="Hello! I'm Aura, your IoT troubleshooting assistant. How can I help you today?")
        st.session_state.messages = [greeting]
        memory_manager.save_message(st.session_state.user_id, new_session_id, greeting)
        
        st.rerun()
    
    st.divider()
    
    # Display previous sessions
    st.markdown("### 📚 Recent Conversations")
    sessions = memory_manager.get_user_sessions(st.session_state.user_id, limit=10)
    
    for session in sessions:
        # Format timestamp
        session_time = datetime.fromtimestamp(session['last_message_at'] / 1000)
        time_str = session_time.strftime("%b %d, %H:%M")
        
        # Show if this is the current session
        is_current = session['session_id'] == st.session_state.session_id
        button_label = f"{'🟢 ' if is_current else ''}  {time_str}"
        
        if st.button(button_label, key=session['session_id'], use_container_width=True, disabled=is_current):
            # Load this session
            st.session_state.session_id = session['session_id']
            st.session_state.messages = memory_manager.load_history(
                st.session_state.user_id,
                session['session_id']
            )
            st.rerun()
    
    st.divider()
    
    # Info section
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Aura** is an AI-powered troubleshooting assistant for IoT devices.
    
    **Features:**
    - 🧠 Long-term memory across sessions
    - 🔍 Knowledge base search
    - 🔄 Multi-step reasoning
    - 📊 Device diagnostics
    """)
    
    # Debug info (expandable)
    with st.expander("🔧 Debug Info"):
        st.write(f"User ID: `{st.session_state.user_id}`")
        st.write(f"Session ID: `{st.session_state.session_id[:8]}...`")
        st.write(f"Messages in memory: {len(st.session_state.messages)}")

# --- Main Chat Interface ---
st.markdown('<p class="main-header">🤖 Aura IoT Troubleshooter</p>', unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    # Skip system messages in the UI
    if isinstance(message, SystemMessage):
        continue
    
    with st.chat_message(message.type):
        st.markdown(message.content)

# --- Handle User Input ---
if prompt := st.chat_input("Describe your issue or ask a question..."):
    # Display user message immediately
    st.chat_message("human").markdown(prompt)
    
    # Add user message to session state
    user_message = HumanMessage(content=prompt)
    st.session_state.messages.append(user_message)
    
    # Display AI response with thinking indicator
    with st.chat_message("ai"):
        with st.spinner("🤔 Aura is analyzing..."):
            try:
                # Prepare input for the LangGraph agent
                inputs = {
                    "chat_history": st.session_state.messages,
                    "user_id": st.session_state.user_id,
                    "session_id": st.session_state.session_id
                }
                
                # Invoke the agent (this may loop through multiple tool calls)
                response = aura_graph.invoke(inputs)
                
                # Extract the final AI response
                final_answer = response["chat_history"][-1]
                
                # Display the response
                st.markdown(final_answer.content)
                
                # Update session state with the AI response
                st.session_state.messages.append(final_answer)
                
                # Save both user message and AI response to database
                memory_manager.save_messages(
                    st.session_state.user_id,
                    st.session_state.session_id,
                    [user_message, final_answer]
                )
                
            except Exception as e:
                error_message = f"⚠️ An error occurred: {str(e)}"
                st.error(error_message)
                
                # Log the error but keep the conversation going
                error_ai_message = AIMessage(content=error_message)
                st.session_state.messages.append(error_ai_message)
    
    # Rerun to update the UI properly
    st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #666;">Powered by LangGraph, Azure OpenAI, and PostgreSQL</p>',
    unsafe_allow_html=True
)
