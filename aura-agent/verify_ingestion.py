#!/usr/bin/env python3
"""
Verification Script for Ingested Data
This script queries the PostgreSQL database to verify the ingested data.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DB_CONNECTION_STRING = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

def print_table(headers, rows):
    """Simple table printer."""
    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))

def verify_ingestion():
    """Query the database and display statistics about ingested data."""
    
    conn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("DATABASE INGESTION VERIFICATION")
    print("="*80 + "\n")
    
    # 1. Check knowledge_chunks table
    print("📄 TEXT CHUNKS")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            document_id,
            COUNT(*) as chunk_count,
            AVG(LENGTH(text_content)) as avg_chunk_length
        FROM knowledge_chunks
        GROUP BY document_id
        ORDER BY document_id;
    """)
    
    chunks_data = cursor.fetchall()
    if chunks_data:
        headers = ["Document ID", "Chunk Count", "Avg Chunk Length"]
        print_table(headers, chunks_data)
        
        # Total chunks
        cursor.execute("SELECT COUNT(*) FROM knowledge_chunks;")
        total_chunks = cursor.fetchone()[0]
        print(f"\n✅ Total text chunks: {total_chunks}")
    else:
        print("❌ No text chunks found in database!")
    
    print()
    
    # 2. Check knowledge_images table
    print("🖼️  IMAGE EMBEDDINGS")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            image_path,
            vector_dims(image_embedding) as vector_dimension
        FROM knowledge_images
        ORDER BY image_path;
    """)
    
    images_data = cursor.fetchall()
    if images_data:
        headers = ["Image Path", "Vector Dimension"]
        print_table(headers, images_data)
        
        # Total images
        cursor.execute("SELECT COUNT(*) FROM knowledge_images;")
        total_images = cursor.fetchone()[0]
        print(f"\n✅ Total image embeddings: {total_images}")
    else:
        print("❌ No image embeddings found in database!")
    
    print()
    
    # 3. Check chunk_image_links table
    print("🔗 CHUNK-IMAGE RELATIONSHIPS")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            ki.image_path,
            COUNT(DISTINCT cil.chunk_id) as linked_chunks
        FROM chunk_image_links cil
        JOIN knowledge_images ki ON cil.image_id = ki.id
        GROUP BY ki.image_path
        ORDER BY ki.image_path;
    """)
    
    links_data = cursor.fetchall()
    if links_data:
        headers = ["Image Path", "Linked to # Chunks"]
        print_table(headers, links_data)
        
        # Total links
        cursor.execute("SELECT COUNT(*) FROM chunk_image_links;")
        total_links = cursor.fetchone()[0]
        print(f"\n✅ Total chunk-image links: {total_links}")
    else:
        print("❌ No chunk-image links found in database!")
    
    print()
    
    # 4. Sample text chunk
    print("📝 SAMPLE TEXT CHUNK")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            document_id,
            chunk_index,
            LEFT(text_content, 200) as preview,
            vector_dims(text_embedding) as embedding_dim
        FROM knowledge_chunks
        LIMIT 1;
    """)
    
    sample = cursor.fetchone()
    if sample:
        print(f"Document: {sample[0]}")
        print(f"Chunk Index: {sample[1]}")
        print(f"Text Preview: {sample[2]}...")
        print(f"Text Embedding Dimension: {sample[3]}")
    
    print()
    
    # 5. Check embedding dimensions
    print("📊 EMBEDDING DIMENSIONS")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            'Text Embeddings' as type,
            vector_dims(text_embedding) as dimension,
            COUNT(*) as count
        FROM knowledge_chunks
        WHERE text_embedding IS NOT NULL
        GROUP BY vector_dims(text_embedding)
        
        UNION ALL
        
        SELECT 
            'Image Embeddings' as type,
            vector_dims(image_embedding) as dimension,
            COUNT(*) as count
        FROM knowledge_images
        WHERE image_embedding IS NOT NULL
        GROUP BY vector_dims(image_embedding);
    """)
    
    dimensions_data = cursor.fetchall()
    if dimensions_data:
        headers = ["Type", "Dimension", "Count"]
        print_table(headers, dimensions_data)
    
    print()
    
    # 6. Test similarity search
    print("🔍 TEST SIMILARITY SEARCH")
    print("-" * 80)
    print("Testing vector similarity search with a sample query...")
    
    # Get a sample embedding
    cursor.execute("SELECT text_embedding FROM knowledge_chunks LIMIT 1;")
    sample_embedding = cursor.fetchone()[0]
    
    # Perform similarity search (cosine distance)
    cursor.execute("""
        SELECT 
            document_id,
            chunk_index,
            LEFT(text_content, 100) as preview,
            text_embedding <=> %s::vector AS distance
        FROM knowledge_chunks
        ORDER BY text_embedding <=> %s::vector
        LIMIT 3;
    """, (sample_embedding, sample_embedding))
    
    search_results = cursor.fetchall()
    if search_results:
        headers = ["Document", "Chunk", "Preview", "Distance"]
        print_table(headers, search_results)
        print("\n✅ Vector similarity search is working!")
    
    print()
    print("="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        verify_ingestion()
    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
