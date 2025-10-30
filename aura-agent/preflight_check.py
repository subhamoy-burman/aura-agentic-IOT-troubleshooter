#!/usr/bin/env python3
"""
Pre-Flight Checks for Aura IoT Troubleshooter Agent
This script validates all critical connections and configurations before running the agent.
"""

import os
import sys
from dotenv import load_dotenv
from typing import Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    """Print error message."""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text: str):
    """Print info message."""
    print(f"{BLUE}ℹ️  {text}{RESET}")


def check_langsmith_config() -> bool:
    """
    Verify LangSmith configuration and test API connection.
    """
    print_info("Checking LangSmith Configuration...")
    
    try:
        api_key = os.getenv("LANGCHAIN_API_KEY")
        endpoint = os.getenv("LANGCHAIN_ENDPOINT")
        project = os.getenv("LANGCHAIN_PROJECT")
        tracing = os.getenv("LANGCHAIN_TRACING_V2")
        
        # Check if variables are set
        if not api_key or api_key == "your_langsmith_api_key_here":
            print_error("LANGCHAIN_API_KEY is not set or is default value")
            return False
        
        if not endpoint:
            print_error("LANGCHAIN_ENDPOINT is not set")
            return False
        
        if not project:
            print_warning("LANGCHAIN_PROJECT is not set (optional but recommended)")
        
        print_success(f"LangSmith API Key: Found (starts with '{api_key[:10]}...')")
        print_success(f"LangSmith Endpoint: {endpoint}")
        print_success(f"LangSmith Project: {project or 'default'}")
        print_success(f"Tracing Enabled: {tracing}")
        
        # Test the connection
        try:
            from langsmith import Client
            client = Client(api_key=api_key, api_url=endpoint)
            
            # Try to list projects (lightweight operation)
            try:
                # This will raise an error if authentication fails
                client.list_projects(limit=1)
                print_success("LangSmith API connection verified!")
                return True
            except Exception as e:
                print_error(f"LangSmith API authentication failed: {str(e)}")
                return False
                
        except ImportError:
            print_warning("LangSmith client not imported, skipping API test")
            return True
        except Exception as e:
            print_error(f"Error testing LangSmith connection: {str(e)}")
            return False
            
    except Exception as e:
        print_error(f"Unexpected error in LangSmith check: {str(e)}")
        return False


def check_postgres_connection() -> bool:
    """
    Verify PostgreSQL connection with pgvector extension.
    """
    print_info("Checking PostgreSQL Connection...")
    
    try:
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")
        
        # Check if variables are set
        if not all([db_user, db_password, db_host, db_name]):
            print_error("PostgreSQL environment variables are not fully configured")
            print_info("Required: DB_USER, DB_PASSWORD, DB_HOST, DB_NAME")
            return False
        
        print_success(f"Database User: {db_user}")
        print_success(f"Database Host: {db_host}:{db_port}")
        print_success(f"Database Name: {db_name}")
        
        # Try to establish connection
        try:
            import psycopg2
            from psycopg2 import sql
            
            connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            print_info(f"Attempting to connect to PostgreSQL...")
            
            conn = psycopg2.connect(
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                database=db_name
            )
            
            cursor = conn.cursor()
            
            # Check PostgreSQL version
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print_success(f"PostgreSQL connected: {version.split(',')[0]}")
            
            # Check if pgvector extension is installed
            cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            vector_ext = cursor.fetchone()
            
            if vector_ext:
                print_success("pgvector extension is installed ✓")
            else:
                print_warning("pgvector extension not found - attempting to install...")
                try:
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    conn.commit()
                    print_success("pgvector extension installed successfully!")
                except Exception as e:
                    print_error(f"Could not install pgvector: {str(e)}")
                    print_info("You may need to install it manually with: CREATE EXTENSION vector;")
            
            # Test a simple query
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            if result[0] == 1:
                print_success("Test query executed successfully!")
            
            cursor.close()
            conn.close()
            
            return True
            
        except ImportError:
            print_error("psycopg2 not installed. Installing...")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
                print_success("psycopg2 installed. Please run the check again.")
                return False
            except Exception as e:
                print_error(f"Failed to install psycopg2: {str(e)}")
                return False
                
        except psycopg2.OperationalError as e:
            print_error(f"PostgreSQL connection failed: {str(e)}")
            print_info("Make sure your Docker container is running:")
            print_info("  docker ps")
            return False
            
        except Exception as e:
            print_error(f"Error connecting to PostgreSQL: {str(e)}")
            return False
            
    except Exception as e:
        print_error(f"Unexpected error in PostgreSQL check: {str(e)}")
        return False


def check_azure_openai_connection() -> bool:
    """
    Verify Azure OpenAI configuration and test API connection.
    """
    print_info("Checking Azure OpenAI Connection...")
    
    try:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
        
        # Check if variables are set
        missing_vars = []
        if not api_key or api_key == "your_api_key_here":
            missing_vars.append("AZURE_OPENAI_API_KEY")
        if not endpoint:
            missing_vars.append("AZURE_OPENAI_ENDPOINT")
        if not api_version:
            missing_vars.append("AZURE_OPENAI_API_VERSION")
        if not chat_deployment:
            missing_vars.append("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        if not embedding_deployment:
            missing_vars.append("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
        
        if missing_vars:
            print_error(f"Missing Azure OpenAI variables: {', '.join(missing_vars)}")
            return False
        
        print_success(f"Azure OpenAI Endpoint: {endpoint}")
        print_success(f"API Version: {api_version}")
        print_success(f"Chat Deployment: {chat_deployment}")
        print_success(f"Embedding Deployment: {embedding_deployment}")
        print_success(f"API Key: Found (starts with '{api_key[:10]}...')")
        
        # Test the connection with Azure OpenAI
        try:
            from openai import AzureOpenAI
            
            print_info("Testing Azure OpenAI chat completion...")
            
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            
            # Test chat completion with a simple prompt
            try:
                response = client.chat.completions.create(
                    model=chat_deployment,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Say 'Hello' if you can hear me."}
                    ],
                    max_tokens=10
                )
                
                if response.choices and response.choices[0].message.content:
                    print_success(f"Chat completion test successful! Response: '{response.choices[0].message.content.strip()}'")
                else:
                    print_warning("Chat completion returned empty response")
                    
            except Exception as e:
                print_error(f"Chat completion test failed: {str(e)}")
                return False
            
            # Test embeddings
            print_info("Testing Azure OpenAI embeddings...")
            try:
                embedding_response = client.embeddings.create(
                    model=embedding_deployment,
                    input="Test embedding"
                )
                
                if embedding_response.data and len(embedding_response.data) > 0:
                    embedding_dim = len(embedding_response.data[0].embedding)
                    print_success(f"Embedding test successful! Dimension: {embedding_dim}")
                else:
                    print_warning("Embedding returned empty response")
                    
            except Exception as e:
                print_error(f"Embedding test failed: {str(e)}")
                print_warning("Chat model works, but embedding model may need attention")
                # Don't fail the check if only embeddings fail
            
            return True
            
        except ImportError:
            print_error("OpenAI library not properly installed")
            return False
            
        except Exception as e:
            print_error(f"Error testing Azure OpenAI connection: {str(e)}")
            return False
            
    except Exception as e:
        print_error(f"Unexpected error in Azure OpenAI check: {str(e)}")
        return False


def check_environment_file() -> bool:
    """Check if .env file exists and is readable."""
    print_info("Checking .env file...")
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if not os.path.exists(env_path):
        print_error(f".env file not found at {env_path}")
        return False
    
    print_success(f".env file found at {env_path}")
    
    # Check file permissions
    if not os.access(env_path, os.R_OK):
        print_error(".env file is not readable")
        return False
    
    print_success(".env file is readable")
    return True


def check_required_packages() -> bool:
    """Check if all required packages are installed."""
    print_info("Checking required packages...")
    
    required_packages = [
        ("langchain", "langchain"),
        ("langgraph", "langgraph"),
        ("langsmith", "langsmith"),
        ("openai", "openai"),
        ("python-dotenv", "dotenv"),
        ("chromadb", "chromadb")
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print_success(f"{package_name} is installed")
        except ImportError:
            print_error(f"{package_name} is NOT installed")
            missing_packages.append(package_name)
    
    if missing_packages:
        print_error(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Run: pip install -r requirements.txt")
        return False
    
    return True


# --- Main Test Function ---
def run_pre_flight_checks():
    """
    Executes a series of checks to ensure the development environment is configured correctly.
    """
    print_header("🚀 Aura Agent Pre-Flight Checks")
    
    # Load environment variables
    load_dotenv()
    print_success("Environment variables loaded from .env file\n")
    
    # Check .env file
    env_file_ok = check_environment_file()
    print()
    
    # Check required packages
    packages_ok = check_required_packages()
    print()
    
    # Run main checks sequentially
    is_langsmith_ok = check_langsmith_config()
    print()
    
    is_postgres_ok = check_postgres_connection()
    print()
    
    is_azure_ok = check_azure_openai_connection()
    print()
    
    # Print summary
    print_header("📊 Pre-Flight Check Summary")
    
    results = {
        "Environment File": env_file_ok,
        "Required Packages": packages_ok,
        "LangSmith Configuration": is_langsmith_ok,
        "PostgreSQL Connection": is_postgres_ok,
        "Azure OpenAI Connection": is_azure_ok
    }
    
    for check_name, status in results.items():
        status_icon = "✅" if status else "❌"
        status_text = "PASSED" if status else "FAILED"
        color = GREEN if status else RED
        print(f"{color}{status_icon} {check_name}: {status_text}{RESET}")
    
    print()
    
    all_passed = all(results.values())
    
    if all_passed:
        print_header("🎉 All checks passed! You are ready to start building.")
        return 0
    else:
        print_header("⚠️  Some checks failed. Please review the error messages above.")
        print_info("Common fixes:")
        print_info("  • Make sure git PostgreSQL container is running")
        print_info("  • Verify all API keys in .env file")
        print_info("  • Check network connectivity")
        print_info("  • Ensure all packages are installed: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(run_pre_flight_checks())
