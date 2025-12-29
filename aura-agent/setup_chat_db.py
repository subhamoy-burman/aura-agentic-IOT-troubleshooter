"""
One-time Database Setup Script for Chat History Tables

This script creates the necessary PostgreSQL tables for storing chat history
and session metadata in your existing database.

Usage:
    python aura-agent/setup_chat_db.py

Note: This uses your existing PostgreSQL database (the same one used for pgvector).
No new database or service required!
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CREATE_TABLES_SQL = """
-- Table for storing individual chat messages
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    timestamp BIGINT NOT NULL,
    message_type VARCHAR(10) NOT NULL CHECK (message_type IN ('human', 'ai')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast retrieval
CREATE INDEX IF NOT EXISTS idx_user_session ON chat_history(user_id, session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_session ON chat_history(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_user_timestamp ON chat_history(user_id, timestamp DESC);

-- Table for storing session metadata
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at BIGINT NOT NULL,
    last_message_at BIGINT NOT NULL,
    title TEXT DEFAULT 'New Conversation',
    metadata JSONB
);

-- Index for listing user sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions ON chat_sessions(user_id, last_message_at DESC);

-- Add a comment to describe the schema
COMMENT ON TABLE chat_history IS 'Stores all chat messages for long-term memory';
COMMENT ON TABLE chat_sessions IS 'Stores session metadata for conversation management';
"""

def main():
    """Create the chat history tables in the existing PostgreSQL database."""
    
    # Validate environment variables
    required_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nMake sure your .env file contains all database configuration.")
        sys.exit(1)
    
    # Connect to PostgreSQL
    print("Connecting to PostgreSQL database...")
    print(f"Host: {os.environ.get('DB_HOST')}")
    print(f"Database: {os.environ.get('DB_NAME')}")
    
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT")),
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD")
        )
        
        print("✅ Connected successfully!\n")
        
        # Create tables
        print("Creating chat history tables...")
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLES_SQL)
            conn.commit()
        
        print("✅ Tables created successfully!\n")
        
        # Verify tables were created
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('chat_history', 'chat_sessions')
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            
            print("Verified tables in database:")
            for table in tables:
                print(f"  ✓ {table[0]}")
        
        conn.close()
        
        print("\n" + "="*60)
        print("🎉 Setup Complete!")
        print("="*60)
        print("\nYour PostgreSQL database now has:")
        print("  • chat_history table - stores all messages")
        print("  • chat_sessions table - tracks conversation sessions")
        print("\nYou can now run your Streamlit app with persistent memory!")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check that PostgreSQL is running")
        print("  2. Verify your .env file has correct credentials")
        print("  3. Ensure the database exists")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
