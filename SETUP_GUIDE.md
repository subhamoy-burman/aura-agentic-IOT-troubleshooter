# 🚀 Aura IoT Troubleshooter - Setup & Deployment Guide

## What Was Implemented

You now have a complete, production-ready conversational AI agent with:

✅ **Long-term Memory** - Conversations persist in PostgreSQL across sessions  
✅ **Conversation Windowing** - Only last 20 messages sent to LLM (prevents token overflow)  
✅ **Multi-turn Reasoning** - Agent can call multiple tools in one response  
✅ **Session Management** - Browse and switch between previous conversations  
✅ **Error Handling** - Graceful failures with lazy initialization  
✅ **Streamlit UI** - Beautiful, responsive web interface  

---

## 📂 File Changes Summary

### New Files Created:
- `app.py` - Streamlit web interface with persistence
- `aura-agent/setup_chat_db.py` - Database setup script
- `aura-agent/src/memory_manager.py` - PostgreSQL-based memory system

### Files Updated:
- `aura-agent/src/agent_state.py` - Added state reducers and user/session tracking
- `aura-agent/src/tools.py` - Added lazy initialization and error handling
- `aura-agent/src/graph.py` - Updated for user context tracking
- `aura-agent/requirements.txt` - Added streamlit and langchain-openai

---

## 🛠️ Installation & Setup

### Step 1: Install Dependencies

```powershell
# Activate your virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Install/update all dependencies
pip install -r aura-agent\requirements.txt
```

### Step 2: Setup Database Tables

Run the setup script to create the chat history tables:

```powershell
python aura-agent\setup_chat_db.py
```

**Expected Output:**
```
Connecting to PostgreSQL database...
Host: your-db-host.postgres.database.azure.com
Database: your-db-name
✅ Connected successfully!

Creating chat history tables...
✅ Tables created successfully!

Verified tables in database:
  ✓ chat_history
  ✓ chat_sessions

🎉 Setup Complete!
```

### Step 3: Verify Knowledge Base Ingestion

Make sure your troubleshooting guides are already ingested into pgvector:

```powershell
cd aura-agent
python verify_ingestion.py
```

If not ingested yet, run:
```powershell
python ingest.py
```

---

## 🚀 Running the Application

### Start the Streamlit App:

```powershell
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

---

## 🎯 Testing the Complete System

### Test 1: Basic Conversation with Memory

1. **Start the app** and ask:
   ```
   My vacuum cleaner shows error E-205
   ```

2. **Agent should:**
   - Call `search_troubleshooting_guides("E-205")`
   - Return troubleshooting steps from knowledge base

3. **Follow up with:**
   ```
   How long will that take?
   ```

4. **Verify:**
   - Agent remembers context (knows "that" refers to E-205)
   - No need to repeat yourself

### Test 2: Session Persistence

1. **Have a conversation** (ask 3-4 questions)
2. **Close the browser tab**
3. **Reopen** `http://localhost:8501`
4. **Verify:**
   - Conversation history is still there
   - You can continue where you left off

### Test 3: Multiple Sessions

1. **Click "Start New Conversation"** in the sidebar
2. **Have a different conversation**
3. **Switch back** to the first session using the sidebar
4. **Verify:**
   - Previous conversations are intact
   - Each session maintains separate context

### Test 4: Conversation Window (Advanced)

1. **Have a very long conversation** (15+ turns)
2. **Check the terminal/logs** for agent behavior
3. **Verify:**
   - Agent only processes last 20 messages
   - Older messages are not sent to LLM
   - Database still stores ALL messages

---

## 🔍 Understanding the Architecture

### The Three-Layer Memory System:

```
┌─────────────────────────────────────┐
│  Browser Session (Streamlit)        │  ← Temporary, current tab only
│  st.session_state.messages          │
└─────────────────────────────────────┘
                ↕ (sync)
┌─────────────────────────────────────┐
│  Agent Working Memory (LangGraph)   │  ← Temporary, one invocation
│  AgentState.chat_history            │
└─────────────────────────────────────┘
                ↕ (load/save)
┌─────────────────────────────────────┐
│  Database (PostgreSQL)               │  ← Permanent, all users
│  chat_history + chat_sessions        │
└─────────────────────────────────────┘
```

### Data Flow on Each User Message:

1. **User types message** → Streamlit captures input
2. **Load history from DB** → Get last 20 messages (conversation window)
3. **Invoke LangGraph agent** → Agent reasons and calls tools
4. **Agent loops** → May call multiple tools before responding
5. **Get final response** → Extract AI's final answer
6. **Save to database** → Persist user message + AI response
7. **Update UI** → Display response to user

---

## 🐛 Troubleshooting

### Issue: "Failed to connect to database"
**Solution:**
- Check your `.env` file has correct PostgreSQL credentials
- Verify PostgreSQL is running
- Test connection: `python aura-agent/setup_chat_db.py`

### Issue: "Module 'langchain_openai' not found"
**Solution:**
```powershell
pip install langchain-openai
```

### Issue: "Table 'chat_history' does not exist"
**Solution:**
```powershell
python aura-agent/setup_chat_db.py
```

### Issue: Agent doesn't find any documents
**Solution:**
- Verify knowledge base ingestion:
  ```powershell
  cd aura-agent
  python verify_ingestion.py
  ```
- If empty, run ingestion:
  ```powershell
  python ingest.py
  ```

### Issue: Streamlit shows errors about state
**Solution:**
- Clear Streamlit cache: In the browser, click hamburger menu → "Clear cache"
- Restart the app

---

## 📊 Database Schema Reference

### Table: `chat_history`
Stores all individual messages:

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| user_id | VARCHAR(255) | User identifier |
| session_id | VARCHAR(255) | Session identifier |
| timestamp | BIGINT | Unix timestamp (ms) |
| message_type | VARCHAR(10) | 'human' or 'ai' |
| content | TEXT | Message content |
| tool_calls | JSONB | Tool invocations (nullable) |
| metadata | JSONB | Extra data (nullable) |

### Table: `chat_sessions`
Stores session metadata:

| Column | Type | Description |
|--------|------|-------------|
| session_id | VARCHAR(255) | Primary key |
| user_id | VARCHAR(255) | User identifier |
| created_at | BIGINT | Session start time |
| last_message_at | BIGINT | Last activity time |
| title | TEXT | Session title |
| metadata | JSONB | Extra data (nullable) |

---

## 🎨 UI Features

### Main Chat Interface:
- Message history display
- Typing indicator while agent thinks
- Error handling with user-friendly messages
- Auto-scroll to latest message

### Sidebar Features:
- **New Conversation** - Start fresh session
- **Recent Conversations** - Browse last 10 sessions
- **About** - Feature overview
- **Debug Info** - Technical details (expandable)

---

## 🔐 Environment Variables Required

Make sure your `.env` file contains:

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002

# PostgreSQL
DB_HOST=your-db-host.postgres.database.azure.com
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

---

## 🚦 Next Steps

### Immediate:
1. ✅ Run `setup_chat_db.py` to create tables
2. ✅ Start app with `streamlit run app.py`
3. ✅ Test basic conversation flow
4. ✅ Verify persistence by closing/reopening browser

### Future Enhancements:
- [ ] Add user authentication (Azure AD, OAuth)
- [ ] Implement conversation summarization for 50+ messages
- [ ] Add export conversation feature (PDF/Markdown)
- [ ] Implement conversation search
- [ ] Add analytics dashboard
- [ ] Deploy to Azure Web Apps

---

## 📝 Key Differences from Original Design

| Aspect | Original Plan | Implementation |
|--------|---------------|----------------|
| Storage | DynamoDB | PostgreSQL (reuses existing DB) |
| Setup | AWS Console | Simple Python script |
| Cost | Pay-per-request | Free (existing DB) |
| Complexity | Separate service | Single database |

---

## 🎉 You're Ready!

Your Aura agent now has:
- **Memory that persists** across sessions
- **Smart windowing** to prevent token overflow
- **Beautiful UI** for easy interaction
- **Robust error handling** for production use

Run `streamlit run app.py` and start troubleshooting! 🚀
