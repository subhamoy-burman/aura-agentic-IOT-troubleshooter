# Tools and Functions for the Aura Agent
# This file will contain all the tools and functions used by the agent

from langchain.tools import BaseTool
from typing import Type, Optional, Dict, Any
import os
from langchain.tools import tool
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector

CONNECTION_STRING = PGVector.connection_string_from_db_params(
    driver="psycopg2",
    host=os.environ.get("DB_HOST"),
    port=int(os.environ.get("DB_PORT")),
    database=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
)

COLLECTION_NAME = "aura_iot_troubleshooting_guides"

embeddings = AzureOpenAIEmbeddings(azure_deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"))

vector_store = PGVector(
    connection_string=CONNECTION_STRING,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3}) # Retrieve top 3 chunks

@tool
def search_troubleshooting_guides(query: str) -> str:
    """
    Searches the knowledge base for troubleshooting guides related to a specific problem or error code.
    Use this to find solutions for user issues.
    """
    print(f"--- RAG TOOL: Searching docs for '{query}' ---")
    docs = retriever.invoke(query)
    # Format the retrieved documents into a single string for the LLM
    return "\n\n".join([f"Source: {doc.metadata.get('source', 'N/A')}\nContent: {doc.page_content}" for doc in docs])
