"""
Step 6: Index ICICI HFC .txt documents into ChromaDB
Location: tcs_poc/index_icici_docs.py

SAVES IT TO:
Folder: ChromaDB persist directory (as defined in config)
Collection: Saves to ChromaDB's banking_collection
Note: Indexes documents into vector database, no separate output files
"""

import os
import glob
import warnings
from pathlib import Path
from vectorstore.setup_chroma import ChromaDBSetup
from config import BANKING_COLLECTION

#  SILENCE TENSORFLOW WARNINGS
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore', category=DeprecationWarning)


def load_icici_documents(corpus_dir="./corpus"):
    """Load all ICICI HFC .txt files from corpus directory"""
    documents = []
    
    if not os.path.exists(corpus_dir):
        print(f" Error: {corpus_dir} not found!")
        return documents
    
    txt_files = glob.glob(f"{corpus_dir}/*.txt")
    
    if not txt_files:
        print(f" No .txt files found in {corpus_dir}")
        return documents
    
    print(f"\n Loading documents from {corpus_dir}...")
    print(f"Found {len(txt_files)} .txt files\n")
    
    for filepath in txt_files:
        filename = os.path.basename(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                content = clean_document_content(content, filename) #new
            
            if not content:
                print(f" Skipping empty file: {filename}")
                continue
            
            metadata = extract_metadata_from_filename(filename)
            
            documents.append({
                'content': content,
                'metadata': metadata,
                'filename': filename
            })
            
            print(f" Loaded: {filename}")
            print(f"   Type: {metadata['doc_type']} | Loan: {metadata['loan_type']}")
            
        except Exception as e:
            print(f" Error loading {filename}: {str(e)}")
    
    return documents


def extract_metadata_from_filename(filename):
    """Extract metadata from ICICI HFC filename patterns"""
    filename_lower = filename.lower()
    
    if "salaried" in filename_lower:
        doc_type = "salaried"
    elif "self_employed" in filename_lower or "self-employed" in filename_lower:
        doc_type = "self_employed"
    elif "prime" in filename_lower:
        doc_type = "prime"
    elif "knowledge_hub" in filename_lower:
        doc_type = "knowledge_hub"
    else:
        doc_type = "general"
    
    if "top_up" in filename_lower or "top-up" in filename_lower:
        loan_type = "top_up"
    elif "balance_transfer" in filename_lower or "balance-transfer" in filename_lower:
        loan_type = "balance_transfer"
    elif "plot" in filename_lower:
        loan_type = "plot_loan"
    elif "insta" in filename_lower:
        loan_type = "insta_top_up"
    elif "apply" in filename_lower or "application" in filename_lower:
        loan_type = "application"
    elif "eligibility" in filename_lower:
        loan_type = "eligibility"
    elif "home-loan" in filename_lower or "home_loan" in filename_lower:
        loan_type = "general_info"
    else:
        loan_type = "new_loan"
    
    return {
        'source': filename,
        'doc_type': doc_type,
        'loan_type': loan_type,
        'bank': 'ICICI HFC',
        'category': 'home_loan',
        'file_type': 'txt'
    }
def clean_document_content(content, filename):
    """Remove noise from document content for better embeddings"""
    lines = content.split('\n')
    cleaned_lines = []
    
    # Remove filename if it's the first line
    filename_base = filename.replace('.txt', '').replace('_', ' ').lower()
    
    for line in lines:
        line = line.strip()
        
        # Skip if line is just the filename
        if line.lower() == filename_base:
            continue
        
        # Skip very short lines (likely formatting artifacts)
        if len(line) < 3:
            continue
        
        # Skip lines that are just separators
        if all(c in '-_=*#' for c in line):
            continue
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def chunk_document(content, chunk_size=2500, overlap=300):
    """
    Split large documents into overlapping chunks
     FIXED: Simple, reliable chunking without bugs
    """
    # Small documents don't need chunking
    if len(content) <= chunk_size:
        return [content]
    
    chunks = []
    start = 0
    
    while start < len(content):
        # Calculate end position
        end = start + chunk_size
        
        # Don't exceed document length
        if end >= len(content):
            # Last chunk - take everything remaining
            chunks.append(content[start:].strip())
            break
        
        # Try to break at sentence boundary
        chunk_text = content[start:end]
        best_break = -1
        
        # Look for sentence delimiters in last 40% of chunk
        search_start = int(len(chunk_text) * 0.6)
        search_text = chunk_text[search_start:]
        
        for delimiter in ['. ', '\n\n', '? ', '! ', '\n']:
            pos = search_text.rfind(delimiter)
            if pos != -1:
                best_break = search_start + pos + len(delimiter)
                break
        
        # If found good break point, use it
        if best_break > 0:
            end = start + best_break
        
        # Extract and add chunk
        chunk = content[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move to next position with overlap
        start = end - overlap
        
        # Ensure we always make progress
        if start <= 0:
            start = end
    
    return chunks


def index_icici_documents(corpus_dir="./corpus", use_chunking=True):
    """Main function to index ICICI HFC documents into ChromaDB"""
    
    print("=" * 70)
    print("STEP 6: INDEXING ICICI HFC DOCUMENTS")
    print("=" * 70)
    
    # Initialize ChromaDB
    print("\n Initializing ChromaDB...")
    chroma_setup = ChromaDBSetup()
    
    # Get collection
    collection_name = BANKING_COLLECTION
    collection = chroma_setup.client.get_or_create_collection(name=collection_name)
    
    print(f" Collection '{collection_name}' ready")
    print(f"   Current document count: {collection.count()}")
    
    # Load documents
    documents = load_icici_documents(corpus_dir)
    
    if not documents:
        print("\n No documents to index!")
        return
    
    # Process and index documents
    print(f"\n Processing {len(documents)} documents...")
    
    all_chunks = []
    all_metadatas = []
    all_ids = []
    
    doc_count = 0
    chunk_count = 0
    
    for doc in documents:
        content = doc['content']
        metadata = doc['metadata']
        filename = doc['filename']
        
        try:
            if use_chunking:
                chunks = chunk_document(content, chunk_size=2500, overlap=300)
            else:
                chunks = [content]
            
            # Sanity check
            if len(chunks) > 50:
                print(f"WARNING: {filename} has {len(chunks)} chunks (doc length: {len(content)})")
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename.replace('.txt', '')}_{i}"
                
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = i
                chunk_metadata['total_chunks'] = len(chunks)
                chunk_metadata['chunk_id'] = chunk_id
                
                all_chunks.append(chunk)
                all_metadatas.append(chunk_metadata)
                all_ids.append(chunk_id)
                
                chunk_count += 1
            
            doc_count += 1
            print(f"    {filename}: {len(chunks)} chunks")
            
        except Exception as e:
            print(f"    Error processing {filename}: {str(e)}")
            continue
    
    # Batch index to ChromaDB
    print(f"\n Indexing {chunk_count} chunks into ChromaDB...")
    
    try:
        collection.add(
            documents=all_chunks,
            metadatas=all_metadatas,
            ids=all_ids
        )
        
        print(f"\n{'=' * 70}")
        print(f" SUCCESS! Indexed {doc_count} documents ({chunk_count} chunks)")
        print(f"{'=' * 70}")
        print(f"\n Final Statistics:")
        print(f"Total documents: {doc_count}")
        print(f"Total chunks: {chunk_count}")
        print(f"Collection size: {collection.count()}")
        print(f"Average chunks/doc: {chunk_count/doc_count:.1f}")
        
    except Exception as e:
        print(f"\n Error indexing documents: {str(e)}")
        raise


if __name__ == "__main__":
    CORPUS_DIR = "./corpus"
    USE_CHUNKING = True
    
    index_icici_documents(
        corpus_dir=CORPUS_DIR,
        use_chunking=USE_CHUNKING
    )