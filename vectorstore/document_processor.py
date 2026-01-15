"""
Folder: ChromaDB persist directory
Note: Adds documents to ChromaDB collections, no separate files
"""


# vectorstore/document_processor.py
# Import the chromadb library for vector database operations
import chromadb
# Import Path from pathlib for file path manipulations
from pathlib import Path
# Import PdfReader from pypdf to read PDF files
from pypdf import PdfReader
# Import SentenceTransformer for generating text embeddings
from sentence_transformers import SentenceTransformer
# Import List and Dict for type hinting
from typing import List, Dict
# Import sys to manipulate the Python path
import sys
# Import datetime for timestamping
from datetime import datetime
# Import hashlib for generating hashes (used for deduplication)
import hashlib

# Add the parent directory of this file to the system path so config.py can be imported
sys.path.append(str(Path(__file__).parent.parent))
# Import configuration variables from config.py
from config import (
    CHROMA_PERSIST_DIR, # Directory where ChromaDB persists data
    EMBEDDING_MODEL,    # Name of the embedding model to use
    BANKING_COLLECTION, # Name of the banking collection in ChromaDB
    MARKETING_COLLECTION, # Name of the marketing collection in ChromaDB
    BANK_NAME           # Name of the bank (not used directly in this file)
)


class DocumentProcessor:
    """
    Processes PDF documents and stores them in ChromaDB.
    
    Pipeline:
    1. Extract text from PDF
    2. Split into chunks (with overlap)
    3. Generate embeddings
    4. Store in appropriate collection
    
    Key Concepts:
    - Chunking: Breaking large docs into retrievable pieces
    - Metadata: Storing source info alongside chunks
    - Deduplication: Avoiding duplicate content
    """
    
    def __init__(self):
        """
        Initialize document processor.
        
        Loads:
        - ChromaDB client (connects to existing database)
        - Embedding model (for converting text to vectors)
        - Collections (banking and marketing)
        """
        # Print initialization message
        print("Initializing Document Processor...")
        
        # Connect to an existing ChromaDB instance using the persistent directory
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        
        # Load the sentence transformer embedding model
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Get the banking collection from ChromaDB, using a custom embedding function
        self.banking_collection = self.client.get_collection(
            name=BANKING_COLLECTION,
            embedding_function=self._create_embedding_function()
        )
        
        # Get the marketing collection from ChromaDB, using a custom embedding function
        self.marketing_collection = self.client.get_collection(
            name=MARKETING_COLLECTION,
            embedding_function=self._create_embedding_function()
        )
        
        # Print ready message
        print("Document Processor ready!")
    
    
    def _create_embedding_function(self):
        """
        Create ChromaDB-compatible embedding function.
        
        Same pattern as setup_chroma.py - wraps sentence-transformer
        to match ChromaDB's expected interface.
        
        Returns:
            callable: Function that embeds text
        """
        # Define a function that takes a list of texts and returns their embeddings as lists
        def embed_function(texts):
            embeddings = self.embedding_model.encode(texts) # Generate embeddings
            return embeddings.tolist() # Convert numpy array to list
        return embed_function # Return the embedding function
    
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            str: Extracted text from all pages
            
        How it works:
        - Opens PDF using pypdf
        - Iterates through each page
        - Extracts text using built-in parser
        - Combines all pages into single string
        """
        # Print which PDF is being read
        print(f"Reading PDF: {pdf_path}")
        
        try:
            # Create a PdfReader object for the given PDF path
            reader = PdfReader(pdf_path)
            text = "" # Initialize an empty string to hold all text
            
            # Loop through each page in the PDF
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() # Extract text from the page
                text += page_text + "\n" # Add the text and a newline
                
                # Print progress every 10 pages
                if page_num % 10 == 0:
                    print(f"   Processed {page_num}/{len(reader.pages)} pages")
            
            # Print summary of extraction
            print(f"Extracted {len(text)} characters from {len(reader.pages)} pages")
            return text # Return the combined text
            
        except Exception as e:
            # Print error if PDF reading fails
            print(f"Error reading PDF: {e}")
            return "" # Return empty string on failure
    
    
    def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 800, 
        overlap: int = 200
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text (str): Full document text
            chunk_size (int): Target size of each chunk (chars)
            overlap (int): Overlap between consecutive chunks (chars)
            
        Returns:
            List[str]: List of text chunks
            
        Why these defaults?
        - 800 chars ≈ 150-200 words (good context size)
        - 200 char overlap ensures continuity
        - Tested on banking documents for optimal retrieval
        
        Algorithm:
        1. Start at position 0
        2. Take chunk_size characters
        3. Move forward by (chunk_size - overlap)
        4. Repeat until end of text
        """
        chunks = [] # List to store text chunks
        start = 0 # Start index for chunking
        text_length = len(text) # Total length of the text
        
        # Loop until the start index reaches the end of the text
        while start < text_length:
            # Calculate end index for the chunk
            end = start + chunk_size
            # Extract the chunk
            chunk = text[start:end]
            
            # Only add chunk if it has more than 50 non-whitespace characters
            if len(chunk.strip()) > 50:
                chunks.append(chunk.strip())
            
            # Move start index forward by (chunk_size - overlap)
            start += (chunk_size - overlap)
        
        # Print how many chunks were created
        print(f"Created {len(chunks)} chunks from text")
        return chunks # Return the list of chunks
    
    
    def generate_chunk_id(self, chunk_text: str, source: str, index: int) -> str:
        """
        Generate unique ID for each chunk.
        
        Args:
            chunk_text (str): The chunk content
            source (str): Source filename
            index (int): Chunk index in document
            
        Returns:
            str: Unique identifier
            
        Why hash-based IDs?
        - Deduplication: Same content = same ID
        - Reproducibility: Re-processing same PDF generates same IDs
        - No collisions: Hash ensures uniqueness
        
        Format: {source_name}_{index}_{hash}
        Example: icici_homeloan_0_a3f5b2c1
        """
        # Create a hash of the chunk content (first 8 chars of md5)
        content_hash = hashlib.md5(chunk_text.encode()).hexdigest()[:8]
        
        # Clean the source filename (remove extension, lowercase, replace spaces)
        clean_source = Path(source).stem.lower().replace(" ", "_")
        
        # Return the formatted chunk ID
        return f"{clean_source}_{index}_{content_hash}"
    
    
    def process_pdf(
        self, 
        pdf_path: str, 
        collection_name: str = "banking",
        metadata: Dict = None
    ) -> int:
        """
        Complete pipeline: PDF → chunks → ChromaDB
        
        Args:
            pdf_path (str): Path to PDF file
            collection_name (str): "banking" or "marketing"
            metadata (Dict): Additional metadata (e.g., {"bank": "ICICI"})
            
        Returns:
            int: Number of chunks added
            
        Pipeline:
        1. Extract text from PDF
        2. Chunk the text
        3. Generate embeddings (handled by ChromaDB)
        4. Store with metadata
        """
        # Print a separator and processing message
        print(f"\n{'='*60}")
        print(f"Processing: {pdf_path}")
        print(f"{'='*60}\n")
        
        # Step 1: Extract text from the PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            # If no text was extracted, skip processing
            print(" No text extracted. Skipping.")
            return 0
        
        # Step 2: Split the text into chunks
        chunks = self.chunk_text(text)
        if not chunks:
            # If no chunks were created, skip processing
            print(" No chunks created. Skipping.")
            return 0

        # Select the appropriate collection based on collection_name
        collection = (
            self.banking_collection if collection_name == "banking" 
            else self.marketing_collection
        )
        
        # Prepare lists to hold chunk IDs, texts, and metadata
        chunk_ids = []
        chunk_texts = []
        chunk_metadata = []
        
        # Get the source filename from the PDF path
        source_filename = Path(pdf_path).name
        
        # Loop through each chunk and prepare data for ChromaDB
        for idx, chunk in enumerate(chunks):
            # Generate a unique ID for the chunk
            chunk_id = self.generate_chunk_id(chunk, source_filename, idx)
            
            # Create metadata for this chunk
            chunk_meta = {
                "source": source_filename,
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "timestamp": datetime.now().isoformat(),
                "collection": collection_name
            }
            
            # If additional metadata is provided, update the chunk metadata
            if metadata:
                chunk_meta.update(metadata)
            
            # Add the chunk's ID, text, and metadata to their respective lists
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk)
            chunk_metadata.append(chunk_meta)
        
        # Step 3 & 4: Add the chunks to ChromaDB (embeddings are generated automatically)
        print(f"Adding {len(chunks)} chunks to '{collection.name}' collection...")
        
        try:
            # Add the chunks to the collection
            collection.add(
                ids=chunk_ids,
                documents=chunk_texts,
                metadatas=chunk_metadata
            )
            # Print success message and collection size
            print(f"Successfully added {len(chunks)} chunks!")
            print(f"Collection now has {collection.count()} total documents")
            
            return len(chunks) # Return the number of chunks added
            
        except Exception as e:
            # Print error if adding to ChromaDB fails
            print(f"Error adding to ChromaDB: {e}")
            return 0 # Return 0 on failure


# Main function for demo usage

def main():
    """
    Example usage: Process sample PDFs.
    
    In real use, you'll:
    1. Download ICICI/SBI PDFs
    2. Place them in data/banking_docs/
    3. Run this script to ingest them
    """
    # Print demo mode message
    print("🎯 Document Processor - Demo Mode\n")
    
    # Create a DocumentProcessor instance
    processor = DocumentProcessor()
    
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("="*60)
    print("1. Download banking product PDFs from ICICI/SBI websites")
    print("2. Place them in: data/banking_docs/")
    print("3. Uncomment and modify the example below:")
    print()
    print("   # Process ICICI home loan PDF")
    print("   processor.process_pdf(")
    print("       pdf_path='data/banking_docs/icici_homeloan.pdf',")
    print("       collection_name='banking',")
    print("       metadata={'bank': 'ICICI', 'product': 'home_loan'}")
    print("   )")
    print()
    print("   # Process SBI credit card PDF")
    print("   processor.process_pdf(")
    print("       pdf_path='data/banking_docs/sbi_creditcard.pdf',")
    print("       collection_name='banking',")
    print("       metadata={'bank': 'SBI', 'product': 'credit_card'}")
    print("   )")
    print("="*60)


# If this script is run directly, call main()
if __name__ == "__main__":
    main()