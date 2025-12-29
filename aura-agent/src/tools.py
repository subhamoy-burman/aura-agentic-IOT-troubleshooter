# Tools and Functions for the Aura Agent
# This file contains all the tools and functions used by the agent

from langchain.tools import BaseTool
from typing import Type, Optional, Dict, Any
import os
import logging
from langchain.tools import tool
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector

# Configure logging
logger = logging.getLogger(__name__)

class RAGTool:
    """
    Lazy-initialized RAG tool for searching troubleshooting guides.
    
    This class implements lazy initialization to prevent connection failures
    at import time. The vector store connection is only created when first used.
    """
    _vector_store = None
    _retriever = None
    
    @classmethod
    def get_retriever(cls):
        """Get or create the vector store retriever."""
        if cls._retriever is None:
            try:
                logger.info("Initializing pgvector connection...")
                
                CONNECTION_STRING = PGVector.connection_string_from_db_params(
                    driver="psycopg2",
                    host=os.environ.get("DB_HOST"),
                    port=int(os.environ.get("DB_PORT")),
                    database=os.environ.get("DB_NAME"),
                    user=os.environ.get("DB_USER"),
                    password=os.environ.get("DB_PASSWORD"),
                )
                
                COLLECTION_NAME = "aura_iot_troubleshooting_guides"
                
                embeddings = AzureOpenAIEmbeddings(
                    azure_deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
                )
                
                cls._vector_store = PGVector(
                    connection_string=CONNECTION_STRING,
                    collection_name=COLLECTION_NAME,
                    embedding_function=embeddings
                )
                
                cls._retriever = cls._vector_store.as_retriever(search_kwargs={"k": 3})
                logger.info("✅ Vector store initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize vector store: {e}")
                raise
        
        return cls._retriever

@tool
def search_troubleshooting_guides(query: str) -> str:
    """
    Searches the knowledge base for troubleshooting guides related to a specific problem or error code.
    Use this to find solutions for user issues.
    """
    try:
        print(f"--- RAG TOOL: Searching docs for '{query}' ---")
        retriever = RAGTool.get_retriever()
        docs = retriever.invoke(query)
        
        if not docs:
            return "No relevant troubleshooting guides found for this query."
        
        # Format the retrieved documents into a single string for the LLM
        result = "\n\n".join([
            f"Source: {doc.metadata.get('source', 'N/A')}\nContent: {doc.page_content}" 
            for doc in docs
        ])
        return result
        
    except Exception as e:
        logger.error(f"Error in search_troubleshooting_guides: {e}")
        return f"Error searching knowledge base: {str(e)}. Please try rephrasing your query."


@tool
def check_device_connectivity(device_id: str) -> str:
    """
    Checks if a specific IoT device is online and connected to the network.
    Returns the device's connectivity status, signal strength, and last seen time.
    
    Args:
        device_id: The unique identifier of the IoT device (e.g., "AURA-12345")
    """
    print(f"--- DEVICE CONNECTIVITY: Checking device '{device_id}' ---")
    
    # Mock implementation - simulates checking device status
    import random
    from datetime import datetime, timedelta
    
    # Simulate different connectivity scenarios
    scenarios = [
        {
            "status": "online",
            "signal_strength": random.randint(70, 100),
            "last_seen": "Just now",
            "ip_address": f"192.168.1.{random.randint(10, 200)}",
            "uptime": f"{random.randint(1, 48)} hours"
        },
        {
            "status": "offline",
            "signal_strength": 0,
            "last_seen": f"{random.randint(5, 120)} minutes ago",
            "ip_address": "N/A",
            "uptime": "N/A"
        },
        {
            "status": "intermittent",
            "signal_strength": random.randint(20, 50),
            "last_seen": f"{random.randint(1, 5)} seconds ago",
            "ip_address": f"192.168.1.{random.randint(10, 200)}",
            "uptime": f"{random.randint(1, 12)} hours"
        }
    ]
    
    # Select a scenario based on device_id hash for consistency
    scenario_index = hash(device_id) % len(scenarios)
    device_status = scenarios[scenario_index]
    
    result = f"""Device Connectivity Status for {device_id}:
    
Status: {device_status['status'].upper()}
Signal Strength: {device_status['signal_strength']}%
Last Seen: {device_status['last_seen']}
IP Address: {device_status['ip_address']}
Uptime: {device_status['uptime']}

Network Details:
- Connection Type: WiFi 2.4GHz
- MAC Address: {':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])}
- Firmware Version: v2.3.1
"""
    
    return result


@tool
def get_device_error_logs(device_id: str, limit: int = 10) -> str:
    """
    Retrieves recent error logs from a specific IoT device.
    Returns timestamp, error code, severity, and error message.
    
    Args:
        device_id: The unique identifier of the IoT device (e.g., "AURA-12345")
        limit: Maximum number of log entries to return (default: 10)
    """
    print(f"--- DEVICE LOGS: Fetching logs for '{device_id}' (limit: {limit}) ---")
    
    # Mock implementation - simulates retrieving device logs
    import random
    from datetime import datetime, timedelta
    
    # Simulate different error types
    error_types = [
        {"code": "E-101", "severity": "WARNING", "message": "WiFi connection unstable"},
        {"code": "E-205", "severity": "ERROR", "message": "Brush motor stall detected"},
        {"code": "E-300", "severity": "CRITICAL", "message": "Battery voltage low (3.2V)"},
        {"code": "E-401", "severity": "WARNING", "message": "Suction power reduced"},
        {"code": "E-501", "severity": "ERROR", "message": "Water inlet valve timeout"},
        {"code": "E-601", "severity": "WARNING", "message": "Temperature sensor anomaly"},
        {"code": "INFO-001", "severity": "INFO", "message": "Device boot completed successfully"},
        {"code": "INFO-002", "severity": "INFO", "message": "Firmware update check performed"},
    ]
    
    # Generate mock log entries
    logs = []
    base_time = datetime.now()
    
    for i in range(min(limit, 15)):
        # Create timestamp going backwards in time
        log_time = base_time - timedelta(minutes=random.randint(1, 60) * i)
        
        # Select random error type
        error = random.choice(error_types)
        
        log_entry = {
            "timestamp": log_time.strftime("%Y-%m-%d %H:%M:%S"),
            "error_code": error["code"],
            "severity": error["severity"],
            "message": error["message"]
        }
        logs.append(log_entry)
    
    # Format logs as string
    result = f"Device Error Logs for {device_id} (Last {len(logs)} entries):\n\n"
    result += "-" * 80 + "\n"
    
    for log in logs:
        result += f"[{log['timestamp']}] {log['severity']:8s} | {log['error_code']:8s} | {log['message']}\n"
    
    result += "-" * 80 + "\n"
    result += f"\nTotal Entries: {len(logs)}\n"
    result += f"Device ID: {device_id}\n"
    
    return result
