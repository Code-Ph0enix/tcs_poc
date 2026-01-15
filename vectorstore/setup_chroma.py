
"""
vectorstore/setup_chroma.py
Script responsible for initializing and managing ChromaDB vector collections

comments are added for clarity

setup_chroma.py
Folder: ChromaDB persist directory (from config: CHROMA_PERSIST_DIR)

Collections: banking_collection and marketing_collection

Note: Initializes ChromaDB database structure
"""



import chromadb  
# Imports the ChromaDB library used for vector database operations

from chromadb.config import Settings  
# Imports configuration settings class for customizing ChromaDB behavior

from sentence_transformers import SentenceTransformer  
# Imports SentenceTransformer to generate text embeddings

from pathlib import Path  
# Imports Path for robust filesystem path handling

import sys  
# Imports sys to modify Python's module search path at runtime


# Add parent directory to Python path so config.py can be imported
sys.path.append(str(Path(__file__).parent.parent))  
# __file__ → current file path
# parent → vectorstore directory
# parent.parent → project root directory
# append() → allows importing modules from project root

from config import (
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    BANKING_COLLECTION,
    MARKETING_COLLECTION,
    BANK_NAME
)  
# Imports configuration values required for ChromaDB setup
# BANK_NAME is used for descriptive metadata in collections


class ChromaDBSetup:
    """
    Sets up ChromaDB collections for banking and marketing domains.

    Key Concepts:
    - Collections = Logical namespaces for storing vectors
    - Embedding function = Converts text into numerical vectors
    - Persistent client = Ensures data survives application restarts
    """

    def __init__(self):
        """
        Constructor for initializing ChromaDB and the embedding model.

        Execution steps:
        1. Connects to or creates a persistent ChromaDB instance
        2. Loads a sentence-transformer model for embedding generation
        """
        print(f" Initializing ChromaDB at: {CHROMA_PERSIST_DIR}")  
        # Logs the directory where ChromaDB will store persistent data

        # Create a persistent ChromaDB client instance
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,  
            # Specifies the directory where ChromaDB data is stored
            settings=Settings(
                anonymized_telemetry=False,  
                # Disables anonymous usage analytics
                allow_reset=True  
                # Allows collections to be deleted/reset (useful in development)
            )
        )

        print(f" Loading embedding model: {EMBEDDING_MODEL}")  
        # Logs which embedding model is being loaded

        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)  
        # Loads the sentence-transformer model into memory

        print(
            f" Model loaded! Vector dimension: "
            f"{self.embedding_model.get_sentence_embedding_dimension()}"
        )  
        # Prints confirmation along with the embedding vector size


    def create_embedding_function(self):
        """
        Creates an embedding function compatible with ChromaDB.

        Purpose:
        - ChromaDB expects embeddings via a callable interface
        - This method adapts SentenceTransformer to that interface

        Returns:
            callable: Function that maps text → embedding vectors
        """

        def embed_function(texts):
            """
            Converts a list of text strings into vector embeddings.

            Args:
                texts (list[str]): Input text documents

            Returns:
                list[list[float]]: Numerical embedding vectors
            """
            embeddings = self.embedding_model.encode(texts)  
            # Uses the loaded sentence-transformer model to encode text

            return embeddings.tolist()  
            # Converts NumPy array output into a Python list (ChromaDB requirement)

        return embed_function  
        # Returns the embedding function for reuse


    def create_collections(self):
        """
        Creates or loads ChromaDB collections for banking and marketing data.

        Design rationale:
        - Separate collections allow domain-specific retrieval
        - Independent metadata and indexing strategies
        - Cleaner maintenance and updates
        """
        embedding_fn = self.create_embedding_function()  
        # Generates the embedding function to be used by collections

        # =========================
        # Collection 1: Banking Products
        # =========================
        try:
            banking_collection = self.client.get_collection(
                name=BANKING_COLLECTION,  
                # Name of the banking collection
                embedding_function=embedding_fn  
                # Embedding function for vector generation
            )
            print(f" Banking collection '{BANKING_COLLECTION}' already exists")  
            # Confirms that the collection already exists

            print(f"   Documents: {banking_collection.count()}")  
            # Displays the number of documents stored in the collection

        except:
            # Executes if the collection does not exist
            banking_collection = self.client.create_collection(
                name=BANKING_COLLECTION,  
                # Creates a new banking collection
                embedding_function=embedding_fn,  
                # Assigns embedding function
                metadata={
                    "description": (
                        f"Banking products from ICICI, SBI, and {BANK_NAME}"
                    ),  
                    # Human-readable description of the collection
                    "hnsw:space": "cosine"  
                    # Specifies cosine similarity for vector comparison
                }
            )
            print(f" Created new banking collection: '{BANKING_COLLECTION}'")  
            # Logs successful creation of the collection

        # =========================
        # Collection 2: Marketing Campaigns
        # =========================
        try:
            marketing_collection = self.client.get_collection(
                name=MARKETING_COLLECTION,  
                # Name of the marketing collection
                embedding_function=embedding_fn  
                # Embedding function for vector generation
            )
            print(f" Marketing collection '{MARKETING_COLLECTION}' already exists")  
            # Confirms collection already exists

            print(f"   Documents: {marketing_collection.count()}")  
            # Prints number of stored documents

        except:
            # Executes if the marketing collection does not exist
            marketing_collection = self.client.create_collection(
                name=MARKETING_COLLECTION,  
                # Creates a new marketing collection
                embedding_function=embedding_fn,  
                # Assigns embedding function
                metadata={
                    "description": (
                        f"Marketing campaigns and strategies for {BANK_NAME}"
                    ),  
                    # Description for the marketing collection
                    "hnsw:space": "cosine"  
                    # Uses cosine similarity for embeddings
                }
            )
            print(f" Created new marketing collection: '{MARKETING_COLLECTION}'")  
            # Logs creation of the marketing collection

        return banking_collection, marketing_collection  
        # Returns both collection objects for further use


    def get_collection_info(self):
        """
        Prints diagnostic information for all ChromaDB collections.

        Use cases:
        - Debugging setup issues
        - Verifying data persistence
        - Monitoring document counts
        """
        collections = self.client.list_collections()  
        # Retrieves a list of all existing collections

        print("\n" + "=" * 50)  
        # Prints a visual separator

        print("CHROMADB COLLECTION STATUS")  
        # Header for collection status output

        print("=" * 50)  
        # Prints another separator

        if not collections:  
            # Checks if no collections are present
            print("No collections found!")  
            # Warns that no collections exist

        else:
            for collection in collections:  
                # Iterates over each collection
                print(f"\nCollection: {collection.name}")  
                # Prints collection name

                print(f"   Documents: {collection.count()}")  
                # Prints document count

                print(f"   Metadata: {collection.metadata}")  
                # Prints collection metadata

        print("=" * 50 + "\n")  
        # Prints closing separator


def main():
    """
    Entry point for initializing ChromaDB collections.

    Intended usage:
    python vectorstore/setup_chroma.py
    """
    print("Starting ChromaDB Setup...\n")  
    # Logs start of setup process

    setup = ChromaDBSetup()  
    # Instantiates the ChromaDB setup class

    banking_coll, marketing_coll = setup.create_collections()  
    # Creates or loads both banking and marketing collections

    setup.get_collection_info()  
    # Displays current collection status

    print("ChromaDB setup complete!")  
    # Logs successful completion

    print(f"Data will be persisted at: {CHROMA_PERSIST_DIR}")  
    # Prints the directory where data is stored


if __name__ == "__main__":
    main()  
    # Ensures main() runs only when this file is executed directly
# (not when imported as a module)













#  What will work perfectly
# ChromaDB
# PersistentClient
# SentenceTransformers
# Embedding generation
# Vector search
# Banking / Marketing agents
# FastAPI / Uvicorn
# POC agents project is safe.

# ❌ What might break later
# Only if you try to use in the same Python install:
# Selenium automation
# TensorFlow / TensorBoard notebooks
# Old ML scripts relying on TF