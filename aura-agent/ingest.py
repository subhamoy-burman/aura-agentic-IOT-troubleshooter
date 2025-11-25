# Knowledge Base Ingestion Script
# This script will ingest documents from the knowledge_base directory into a vector database

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging
import os
import re
import psycopg2
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- SETUP ---
# Load all environment variables from .env
load_dotenv()


# --- DATABASE CONFIG ---
DB_CONNECTION_STRING = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
KNOWLEDGE_BASE_PATH = "knowledge_base/"


# --- AZURE CLIENT INITIALIZATION ---
# Initialize the client for Text Embeddings (from Azure OpenAI)
text_embeddings_client = AzureOpenAIEmbeddings(
    azure_deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
)


def get_image_embedding_from_azure_vision(image_data: bytes) -> list[float]:

    """
    Generates an embedding for an image using the Azure AI Vision REST API.
    """
    vision_endpoint = os.environ.get("AZURE_COMPUTER_VISION_ENDPOINT")
    vision_key = os.environ.get("AZURE_COMPUTER_VISION_KEY")
    
    if not vision_endpoint or not vision_key:
        print("ERROR: Azure Computer Vision environment variables not set.")
        return None

    # Ensure the endpoint URL doesn't have a trailing slash before appending the path
    base_url = vision_endpoint.rstrip('/')
    
    # --- Updated API Call Based on Documentation ---
    # The specific API endpoint for image vectorization
    api_url = f"{base_url}/computervision/retrieval:vectorizeImage"
    
    # Parameters: Updated API version and specific model version
    params = {
        "api-version": "2024-02-01", # Updated API version from docs
        "model-version": "2023-04-15" # Specific model version (multi-lingual)
    }

    headers = {
        "Content-Type": "application/octet-stream",
        "Ocp-Apim-Subscription-Key": vision_key
    }
    

    try:
        response = requests.post(api_url, params=params, headers=headers, data=image_data, timeout=15)
        response.raise_for_status() 
        return response.json()["vector"]
    except Exception as e:
        print(f"ERROR: Failed to generate image embedding: {e}")
        return None


print("Azure clients initialized.")

def parse_markdown_and_extract_images(file_path):
    """Parses markdown file, extracts image references and cleans the text"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Regex to find image references in markdown ![alt text](image_url)
    image_pattern = r'!\[.*?\]\((.*?)\)'
    image_references = [match.group(1) for match in re.finditer(image_pattern, content)]

    # Create a clean version of text for embedding, replacing images with a placeholder
    text_only = re.sub(image_pattern, '', content)

    return text_only, image_references

def ingest_data():
    """Main function to orchestrate the ingestion of both text and images"""

    conn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()

    # Cache to avoid re-embedd the same image if it is referenced multiple times
    processed_images = {}

    markdown_files = [f for f in os.listdir(KNOWLEDGE_BASE_PATH) if f.endswith('.md')]
    
    for md_file in markdown_files:
        file_path = os.path.join(KNOWLEDGE_BASE_PATH, md_file)
        document_id = os.path.splitext(md_file)[0] 

        print(f"\n Processing document: {document_id} ---")

        #1. Parse and Extract
        clean_text, image_refs = parse_markdown_and_extract_images(file_path)
        print(f"\n Found {len(image_refs)} image references")

        #2. CHUNK and Embed
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        text_chunks = text_splitter.split_text(clean_text)

        if text_chunks:
            print(f"Generating text embeddings for {len(text_chunks)} chunks...")
            text_embeddings = text_embeddings_client.embed_documents(text_chunks)

            chunk_ids = []
            for i, chunk in enumerate(text_chunks):
                cursor.execute(
                    """
                    INSERT INTO knowledge_chunks (document_id, chunk_index, text_content, text_embedding)
                    VALUES (%s, %s, %s, %s) ON CONFLICT (document_id, chunk_index) DO UPDATE SET
                    text_content = EXCLUDED.text_content, text_embedding = EXCLUDED.text_embedding
                    RETURNING id;
                    """,
                    (document_id, i, chunk, text_embeddings[i])

                )
                chunk_id = cursor.fetchone()[0]
                chunk_ids.append(chunk_id)
            print(f"Stored {len(chunk_ids)} text chunks in DB")

        for image_path in image_refs:
            if image_path in processed_images:
                image_id = processed_images[image_path]
            else:
                print(f"Processing new image: {image_path}...")
                full_image_path = os.path.join(KNOWLEDGE_BASE_PATH, image_path)

                if not os.path.exists(full_image_path):
                    print(f" Image file not found: {full_image_path}, skipping...")
                    continue

                with open(full_image_path, "rb") as f:
                    image_data = f.read()

                image_embedding = get_image_embedding_from_azure_vision(image_data)

                cursor.execute(
                     """
                    INSERT INTO knowledge_images (image_path, image_embedding)
                    VALUES (%s, %s) ON CONFLICT (image_path) DO UPDATE SET
                    image_embedding = EXCLUDED.image_embedding
                    RETURNING id;
                    """,
                    (image_path, image_embedding)
                )

                image_id = cursor.fetchone()[0]
                processed_images[image_path] = image_id
                print(f"  Stored image embedding for {image_path}.")

            for chunk_id in chunk_ids:
                cursor.execute(
                    """
                    INSERT INTO chunk_image_links (chunk_id, image_id)
                    VALUES (%s, %s) ON CONFLICT DO NOTHING;
                    """,
                    (chunk_id, image_id)
                )
            print(f"  Linked image {image_path} to text chunks.")

            # Commit all changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()
    print("\n--- Multimodal Ingestion Complete! ---")



if __name__ == "__main__":
    ingest_data()