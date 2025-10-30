#!/usr/bin/env python3
"""
Test script to verify all dependencies are installed correctly
and the Aura IoT Troubleshooter project is ready to use.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all critical packages can be imported."""
    print("🔍 Testing core dependencies...\n")
    
    tests = [
        ("langchain", "LangChain"),
        ("langgraph", "LangGraph"),
        ("langsmith", "LangSmith"),
        ("chromadb", "ChromaDB"),
        ("openai", "OpenAI"),
        ("boto3", "AWS Boto3"),
        ("sentence_transformers", "Sentence Transformers"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("pydantic", "Pydantic"),
        ("dotenv", "Python-dotenv"),
        ("pypdf", "PyPDF"),
        ("docx", "Python-docx"),
        ("markdown", "Markdown"),
        ("click", "Click"),
        ("rich", "Rich"),
        ("typer", "Typer"),
        ("structlog", "Structlog"),
        ("requests", "Requests"),
        ("httpx", "HTTPX"),
        ("pytest", "Pytest"),
        ("black", "Black"),
        ("flake8", "Flake8"),
        ("mypy", "Mypy"),
    ]
    
    failed = []
    for module_name, display_name in tests:
        try:
            __import__(module_name)
            print(f"✓ {display_name:<25} imported successfully")
        except ImportError as e:
            print(f"✗ {display_name:<25} FAILED: {e}")
            failed.append(display_name)
    
    return len(failed) == 0, failed

def check_project_structure():
    """Verify the project structure is in place."""
    print("\n🔍 Checking project structure...\n")
    
    base_path = Path(__file__).parent
    
    required_paths = [
        ("knowledge_base", True),
        ("knowledge_base/E-101-Connectivity.md", False),
        ("knowledge_base/E-205-Brush-Stall.md", False),
        ("knowledge_base/E-300-Battery-Fault.md", False),
        ("knowledge_base/General-Startup-Failure.md", False),
        ("src", True),
        ("src/__init__.py", False),
        ("src/agent_state.py", False),
        ("src/tools.py", False),
        ("src/graph.py", False),
        ("src/main_cli.py", False),
        (".env", False),
        ("requirements.txt", False),
        ("ingest.py", False),
    ]
    
    missing = []
    for path_str, is_dir in required_paths:
        path = base_path / path_str
        if is_dir:
            if path.is_dir():
                print(f"✓ Directory: {path_str}")
            else:
                print(f"✗ Missing directory: {path_str}")
                missing.append(path_str)
        else:
            if path.is_file():
                print(f"✓ File: {path_str}")
            else:
                print(f"✗ Missing file: {path_str}")
                missing.append(path_str)
    
    return len(missing) == 0, missing

def check_src_imports():
    """Check if our source modules can be imported."""
    print("\n🔍 Testing project source modules...\n")
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    tests = [
        ("agent_state", "Agent State Module"),
        ("tools", "Tools Module"),
        ("graph", "Graph Module"),
        ("main_cli", "Main CLI Module"),
    ]
    
    failed = []
    for module_name, display_name in tests:
        try:
            __import__(module_name)
            print(f"✓ {display_name:<25} loaded successfully")
        except Exception as e:
            print(f"✗ {display_name:<25} FAILED: {e}")
            failed.append(display_name)
    
    return len(failed) == 0, failed

def main():
    """Run all tests and display results."""
    print("=" * 70)
    print("🚀 AURA IoT Troubleshooter - Setup Verification")
    print("=" * 70)
    print()
    
    # Test imports
    imports_ok, import_failures = test_imports()
    
    # Check structure
    structure_ok, structure_missing = check_project_structure()
    
    # Check source imports
    src_ok, src_failures = check_src_imports()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    all_ok = imports_ok and structure_ok and src_ok
    
    if imports_ok:
        print("✅ All dependencies installed correctly")
    else:
        print(f"❌ Failed to import: {', '.join(import_failures)}")
    
    if structure_ok:
        print("✅ Project structure is complete")
    else:
        print(f"❌ Missing: {', '.join(structure_missing)}")
    
    if src_ok:
        print("✅ All source modules load successfully")
    else:
        print(f"❌ Failed modules: {', '.join(src_failures)}")
    
    print()
    
    if all_ok:
        print("=" * 70)
        print("🎉 SUCCESS! Your Aura IoT Troubleshooter is ready to use!")
        print("=" * 70)
        print()
        print("📝 Next Steps:")
        print("  1. Configure your .env file with API keys")
        print("  2. Run: python ingest.py (to load knowledge base)")
        print("  3. Run: python src/main_cli.py --help (to see CLI options)")
        print()
        print("🔧 Development Commands:")
        print("  • Format code: black src/")
        print("  • Lint code: flake8 src/")
        print("  • Type check: mypy src/")
        print("  • Run tests: pytest")
        print()
        return 0
    else:
        print("=" * 70)
        print("❌ Setup verification failed. Please check the errors above.")
        print("=" * 70)
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
