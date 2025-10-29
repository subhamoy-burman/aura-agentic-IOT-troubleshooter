# Knowledge Base Ingestion Script
# This script will ingest documents from the knowledge_base directory into a vector database

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_markdown_files(knowledge_base_path: str) -> List[Dict[str, Any]]:
    """Load all markdown files from the knowledge base directory"""
    documents = []
    kb_path = Path(knowledge_base_path)
    
    if not kb_path.exists():
        logger.error(f"Knowledge base path does not exist: {knowledge_base_path}")
        return documents
    
    for md_file in kb_path.glob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append({
                    'filename': md_file.name,
                    'filepath': str(md_file),
                    'content': content
                })
                logger.info(f"Loaded: {md_file.name}")
        except Exception as e:
            logger.error(f"Error loading {md_file}: {e}")
    
    return documents

def ingest_documents():
    """Main ingestion function"""
    logger.info("Starting knowledge base ingestion...")
    
    # Define paths
    current_dir = Path(__file__).parent
    knowledge_base_path = current_dir / "knowledge_base"
    
    # Load documents
    documents = load_markdown_files(str(knowledge_base_path))
    
    if not documents:
        logger.warning("No documents found to ingest")
        return
    
    logger.info(f"Successfully loaded {len(documents)} documents")
    
    # TODO: Implement vector database ingestion
    # This will include:
    # 1. Text chunking
    # 2. Embedding generation
    # 3. Vector database storage (ChromaDB)
    
    logger.info("Ingestion completed")

if __name__ == "__main__":
    ingest_documents()