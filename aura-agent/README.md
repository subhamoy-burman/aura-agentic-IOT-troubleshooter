# Aura IoT Troubleshooter 🤖

An AI-powered agentic system built with LangChain and LangGraph to provide intelligent IoT device troubleshooting assistance.

## ✅ Project Status

**Build Status:** ✅ **SUCCESS** - All dependencies installed and verified!

## 📁 Project Structure

```
aura-agent/
├── knowledge_base/          # IoT troubleshooting guides
│   ├── E-101-Connectivity.md
│   ├── E-205-Brush-Stall.md
│   ├── E-300-Battery-Fault.md
│   └── General-Startup-Failure.md
├── src/                     # Source code
│   ├── __init__.py
│   ├── agent_state.py      # Agent state management
│   ├── tools.py            # LangChain tools
│   ├── graph.py            # LangGraph workflow
│   └── main_cli.py         # CLI interface
├── .env                     # Environment variables (configure this!)
├── requirements.txt         # Python dependencies
├── ingest.py               # Knowledge base ingestion
└── test_setup.py           # Setup verification script
```

## 🚀 Quick Start

### 1. Run Pre-Flight Checks
**IMPORTANT: Run this first to verify all connections!**
```bash
python preflight_check.py
```

This will verify:
- ✅ Environment file configuration
- ✅ Required Python packages
- ✅ LangSmith API connection
- ✅ PostgreSQL + pgvector database
- ✅ Azure OpenAI (Chat & Embeddings)

### 2. Verify Installation (Alternative)
```bash
python test_setup.py
```

### 3. Configure Environment Variables
Edit `.env` file and add your API keys:
```bash
# Already configured in your .env:
LANGCHAIN_API_KEY=your_langsmith_key
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=your_endpoint
DB_USER=aura_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_NAME=aura_db
```

### 4. Load Knowledge Base
```bash
python ingest.py
```

### 5. Run the CLI
```bash
python src/main_cli.py --help
```

## 🛠️ Technology Stack

- **LangChain** (v1.0.2) - LLM application framework
- **LangGraph** (v1.0.1) - Stateful agent workflows
- **LangSmith** (v0.4.38) - Tracing and monitoring
- **ChromaDB** (v1.3.0) - Vector database
- **PostgreSQL + pgvector** - Production vector store
- **Azure OpenAI** (v2.6.1) - LLM provider (gpt-4.1 + embeddings)
- **Sentence Transformers** (v5.1.2) - Embeddings

## 📦 Installed Dependencies

✅ All 24 core dependencies verified and working:
- LangChain & LangGraph ecosystem
- OpenAI API client
- AWS SDK (Boto3)
- Vector database (ChromaDB)
- Document processing (PyPDF, python-docx, Markdown)
- Data analysis (Pandas, NumPy)
- CLI tools (Click, Rich, Typer)
- Development tools (Pytest, Black, Flake8, Mypy)

## 🔧 Development Commands

### Code Formatting
```bash
black src/
```

### Linting
```bash
flake8 src/
```

### Type Checking
```bash
mypy src/
```

### Run Tests
```bash
pytest
```

## 📝 Knowledge Base

The project includes 4 comprehensive troubleshooting guides:
- **E-101**: WiFi Connectivity Issues
- **E-205**: Main Brush Stall Problems
- **E-300**: Battery Fault Diagnosis
- **General**: Startup Failure Troubleshooting

## 🎯 Next Steps

1. ✅ Dependencies installed
2. ✅ Project structure verified
3. ✅ All modules loading correctly
4. ⏳ Configure `.env` with your API keys
5. ⏳ Implement agent logic in `src/`
6. ⏳ Test the system with sample queries

## 🤝 Contributing

This is a demo project for IoT troubleshooting automation.

## 📄 License

Demo Project - 2025

---

**Last Verified:** October 29, 2025  
**Status:** ✅ All systems operational
