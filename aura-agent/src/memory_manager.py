"""
Chat History Manager - PostgreSQL Backend

Manages persistent storage and retrieval of chat history using PostgreSQL.
This enables long-term memory across sessions and implements conversation windowing.

Key Features:
- Load recent conversation history from database
- Save messages incrementally as conversation progresses
- Implement conversation window (limit context sent to LLM)
- Manage multiple sessions per user
- Support session switching and history browsing
"""

import os
import json
import time
import logging
from typing import List
from uuid import uuid4
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage

# Configure logging
logger = logging.getLogger(__name__)

class ChatHistoryManager:
    """
    Manages chat history persistence using PostgreSQL.
    
    This class handles the 3-layer memory architecture:
    1. Load recent history from PostgreSQL (long-term memory)
    2. Provide working context for LangGraph agent (short-term memory)
    3. Save new messages back to PostgreSQL (persistence)
    """
    
    def __init__(self, max_history_messages: int = 20):
        """
        Initialize the chat history manager.
        
        Args:
            max_history_messages: Maximum messages to load from history.
                                 20 messages = 10 conversation turns.
                                 This implements the "conversation window"
                                 to prevent context overflow.
        """
        self.max_history_messages = max_history_messages
        self.connection_params = {
            "host": os.environ.get("DB_HOST"),
            "port": int(os.environ.get("DB_PORT", "5432")),
            "database": os.environ.get("DB_NAME"),
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD")
        }
        logger.info(f"ChatHistoryManager initialized with max_history={max_history_messages}")
    
    def _get_connection(self):
        """Get a PostgreSQL database connection."""
        try:
            return psycopg2.connect(**self.connection_params)
        except psycopg2.OperationalError as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def load_history(self, user_id: str, session_id: str) -> List[BaseMessage]:
        """
        Load the most recent N messages for this user/session from PostgreSQL.
        
        This implements the conversation window - only the last N messages are loaded
        to prevent overwhelming the LLM with too much context.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            List of LangChain message objects (HumanMessage, AIMessage) in chronological order
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT message_type, content, tool_calls, timestamp
                    FROM chat_history
                    WHERE user_id = %s AND session_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (user_id, session_id, self.max_history_messages))
                
                rows = cur.fetchall()
                
            # Convert DB rows to LangChain messages
            # Reverse to get chronological order (oldest first)
            messages = []
            for row in reversed(rows):
                if row['message_type'] == 'human':
                    messages.append(HumanMessage(content=row['content']))
                elif row['message_type'] == 'ai':
                    # Reconstruct AI message with tool calls if present
                    msg = AIMessage(content=row['content'])
                    if row['tool_calls']:
                        msg.tool_calls = row['tool_calls']
                    messages.append(msg)
            
            logger.info(f"Loaded {len(messages)} messages for session {session_id}")
            return messages
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return []  # Return empty list on error to prevent crashes
        finally:
            conn.close()
    
    def save_message(self, user_id: str, session_id: str, message: BaseMessage):
        """
        Save a single message to PostgreSQL.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            message: LangChain message object to save
        """
        self.save_messages(user_id, session_id, [message])
    
    def save_messages(self, user_id: str, session_id: str, messages: List[BaseMessage]):
        """
        Batch save multiple messages to PostgreSQL.
        
        This is more efficient than saving one at a time.
        Also updates the session metadata (last_message_at timestamp).
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            messages: List of LangChain message objects to save
        """
        if not messages:
            return
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Update session metadata
                timestamp = int(time.time() * 1000)
                cur.execute("""
                    INSERT INTO chat_sessions (session_id, user_id, created_at, last_message_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (session_id) 
                    DO UPDATE SET last_message_at = EXCLUDED.last_message_at
                """, (session_id, user_id, timestamp, timestamp))
                
                # Insert messages
                for msg in messages:
                    message_type = 'human' if isinstance(msg, HumanMessage) else 'ai'
                    tool_calls = None
                    
                    # Extract tool calls if present (for AI messages that called tools)
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        tool_calls = Json(msg.tool_calls)
                    
                    cur.execute("""
                        INSERT INTO chat_history 
                        (user_id, session_id, timestamp, message_type, content, tool_calls)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, session_id, timestamp, message_type, msg.content, tool_calls))
                    
                    timestamp += 1  # Ensure unique timestamps for ordering
                
                conn.commit()
                logger.info(f"Saved {len(messages)} messages to session {session_id}")
        except Exception as e:
            logger.error(f"Error saving messages: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def start_new_session(self, user_id: str, title: str = "New Conversation") -> str:
        """
        Generate a new session_id and initialize it in the database.
        
        Args:
            user_id: User identifier
            title: Optional title for the session
            
        Returns:
            New session_id (UUID string)
        """
        session_id = str(uuid4())
        timestamp = int(time.time() * 1000)
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO chat_sessions (session_id, user_id, created_at, last_message_at, title)
                    VALUES (%s, %s, %s, %s, %s)
                """, (session_id, user_id, timestamp, timestamp, title))
                conn.commit()
            
            logger.info(f"Created new session {session_id} for user {user_id}")
            return session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            conn.rollback()
            # Return a UUID anyway so the app doesn't crash
            return str(uuid4())
        finally:
            conn.close()
    
    def get_user_sessions(self, user_id: str, limit: int = 10) -> List[dict]:
        """
        Get recent session metadata for a user.
        
        This powers the "previous conversations" sidebar feature.
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of session dictionaries with metadata:
            [{"session_id": "...", "created_at": 123456789, "title": "..."}, ...]
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT session_id, created_at, last_message_at, title
                    FROM chat_sessions
                    WHERE user_id = %s
                    ORDER BY last_message_at DESC
                    LIMIT %s
                """, (user_id, limit))
                
                sessions = cur.fetchall()
            
            logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")
            return sessions
        except Exception as e:
            logger.error(f"Error retrieving sessions: {e}")
            return []
        finally:
            conn.close()
    
    def prepare_agent_context(self, user_id: str, session_id: str) -> List[BaseMessage]:
        """
        Load history with conversation windowing applied.
        
        This is the main method that should be called before invoking the agent.
        It implements the conversation window strategy to prevent token overflow.
        
        Future enhancement: Add summarization for very long conversations.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Optimized list of messages ready for LLM consumption
        """
        # For now, just return the windowed history
        # Later, you can add summarization here for conversations > 50 messages
        history = self.load_history(user_id, session_id)
        
        # If history is very long, you could summarize older messages here
        # For example:
        # if len(history) > 40:
        #     old_messages = history[:-20]
        #     recent_messages = history[-20:]
        #     summary = self._summarize_messages(old_messages)
        #     return [SystemMessage(content=summary)] + recent_messages
        
        return history
    
    def delete_session(self, session_id: str):
        """
        Delete a session and all its messages.
        
        Use with caution - this permanently removes data!
        
        Args:
            session_id: Session identifier to delete
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Delete messages first (foreign key order)
                cur.execute("DELETE FROM chat_history WHERE session_id = %s", (session_id,))
                # Delete session metadata
                cur.execute("DELETE FROM chat_sessions WHERE session_id = %s", (session_id,))
                conn.commit()
            
            logger.info(f"Deleted session {session_id}")
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            conn.rollback()
        finally:
            conn.close()
