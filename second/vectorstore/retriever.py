"""vectorstore/retriever.py
No direct file output
Note: Retrieves from ChromaDB, returns results in memory
"""

# Import the chromadb library to interact with the vector database
import chromadb

# Import embedding functions utility from chromadb (though not explicitly used in the main logic, it's imported for potential utility)
from chromadb.utils import embedding_functions

# Import SentenceTransformer to convert text queries into vector embeddings
from sentence_transformers import SentenceTransformer

# Import standard typing hints to ensure code clarity and IDE support
from typing import List, Dict, Optional

# Import Path for cross-platform file path handling
from pathlib import Path

# Import sys to modify the python path for importing modules from parent directories
import sys

# Append the parent directory of the current file to sys.path to allow importing 'config.py'
sys.path.append(str(Path(__file__).parent.parent))

# Import configuration constants from the config file located in the parent directory
from config import (
    CHROMA_PERSIST_DIR,    # The path where the database is stored
    EMBEDDING_MODEL,       # The name of the AI model used for embeddings
    BANKING_COLLECTION,    # The name of the banking document collection
    MARKETING_COLLECTION   # The name of the marketing document collection
)


class KnowledgeRetriever:
    """
    Retrieval interface for agents to query ChromaDB.
    
    Responsibilities:
    - Search banking/marketing collections
    - Filter by metadata (bank, product)
    - Format results for agent consumption
    - Handle errors gracefully
    """
    
    def __init__(self):
        """Initialize retriever with ChromaDB connection."""
        # Print a status message indicating initialization has started
        print("🔍 Initializing Knowledge Retriever...")
        
        # Initialize the persistent ChromaDB client pointing to the storage directory
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        
        # Load the sentence transformer model into memory for generating query embeddings
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Start a try block to safely attempt loading the banking collection
        try:
            # Retrieve the banking collection object from the client
            self.banking_collection = self.client.get_collection(
                name=BANKING_COLLECTION
            )
            # Print success message with the count of documents found in the collection
            print(f"Banking collection: {self.banking_collection.count()} documents")
        # Catch any exceptions if the collection does not exist or fails to load
        except Exception as e:
            # Print a warning message with the error details
            print(f"Banking collection not found: {e}")
            # Set the collection attribute to None to indicate it is unavailable
            self.banking_collection = None
        
        # Start a try block to safely attempt loading the marketing collection
        try:
            # Retrieve the marketing collection object from the client
            self.marketing_collection = self.client.get_collection(
                name=MARKETING_COLLECTION
            )
            # Print success message with the count of documents found in the collection
            print(f"Marketing collection: {self.marketing_collection.count()} documents")
        # Catch any exceptions if the marketing collection fails to load
        except Exception as e:
            # Print a warning message with the error details
            print(f"Marketing collection not found: {e}")
            # Set the collection attribute to None to indicate it is unavailable
            self.marketing_collection = None
        
        # Print a final message indicating the retriever is fully initialized
        print("Retriever ready!\n")


    def search_banking(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Search banking products collection."""
        # Check if the banking collection was successfully loaded
        if not self.banking_collection:
            # Print error if collection is missing
            print("Banking collection not available")
            # Return an empty list as no search can be performed
            return []
        
        # Delegate the search to the internal _search_collection method
        return self._search_collection(
            collection=self.banking_collection, # Pass the banking collection object
            query=query,                        # Pass the search query
            n_results=n_results,                # Pass the number of results desired
            filter_metadata=filter_metadata     # Pass any metadata filters
        )
    
    
    def search_marketing(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Search marketing campaigns collection."""
        # Check if the marketing collection was successfully loaded
        if not self.marketing_collection:
            # Print error if collection is missing
            print("Marketing collection not available")
            # Return an empty list as no search can be performed
            return []
        
        # Delegate the search to the internal _search_collection method
        return self._search_collection(
            collection=self.marketing_collection, # Pass the marketing collection object
            query=query,                          # Pass the search query
            n_results=n_results,                  # Pass the number of results desired
            filter_metadata=filter_metadata       # Pass any metadata filters
        )
    
    
    def _search_collection(
        self,
        collection,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Internal method to search any collection."""
        # Start a try block to handle potential database query errors
        try:
            # Perform the query on the specified ChromaDB collection
            results = collection.query(
                query_texts=[query],    # ChromaDB automatically embeds this text
                n_results=n_results,    # Number of nearest neighbors to return
                where=filter_metadata   # SQL-like 'where' clause for metadata filtering
            )
            
            # Initialize a list to hold the cleaned and formatted result dictionaries
            formatted_results = []
            
            # Check if the results dictionary is empty or contains empty lists (no matches found)
            if not results['documents'] or not results['documents'][0]:
                # Print an informational message that no matches were found
                print(f"No results found for query: '{query}'")
                # Return an empty list
                return []
            
            # Iterate through the indices of the returned documents (results structure is list of lists)
            for idx in range(len(results['documents'][0])):
                # Append a structured dictionary for each result to the list
                formatted_results.append({
                    'content': results['documents'][0][idx],      # The actual text content
                    'metadata': results['metadatas'][0][idx],     # The associated metadata
                    'distance': results['distances'][0][idx],     # The vector distance (e.g., L2 or Cosine)
                    'similarity_score': round(1 - results['distances'][0][idx], 3), # specific formula to convert distance to similarity score
                    'id': results['ids'][0][idx]                  # The unique chunk ID
                })
            
            # Return the list of formatted result dictionaries
            return formatted_results
            
        # Catch any exceptions that occur during the query process
        except Exception as e:
            # Print an error message detailing what went wrong
            print(f"Error during search: {e}")
            # Return an empty list on failure
            return []
    
    
    def search_all(
        self,
        query: str,
        n_results_per_collection: int = 3
    ) -> Dict[str, List[Dict]]:
        """Search both banking and marketing collections."""
        # Return a dictionary containing results from both collections
        return {
            'banking': self.search_banking(query, n_results_per_collection), # Search banking
            'marketing': self.search_marketing(query, n_results_per_collection) # Search marketing
        }
    
    
    def get_context_for_agent(
        self,
        query: str,
        collection_type: str = "banking",
        n_results: int = 3
    ) -> str:
        """Get formatted context string for LLM prompts."""
        # Determine which collection to search based on the input type string
        if collection_type == "banking":
            # Execute search on banking collection
            results = self.search_banking(query, n_results)
        elif collection_type == "marketing":
            # Execute search on marketing collection
            results = self.search_marketing(query, n_results)
        else:
            # Handle invalid collection type inputs
            print(f"Unknown collection type: {collection_type}")
            # Return empty string as context
            return ""
        
        # If the search returned no results
        if not results:
            # Return a default string indicating no info was found
            return "No relevant information found in knowledge base."
        
        # Initialize a list to hold formatted string parts
        context_parts = []
        # Iterate through the results with a counter starting at 1
        for idx, result in enumerate(results, start=1):
            # Safe retrieval of source from metadata, default to 'unknown'
            source = result['metadata'].get('source', 'unknown')
            # Retrieve the pre-calculated similarity score
            score = result['similarity_score']
            # Retrieve the main text content
            content = result['content']
            
            # Append a formatted string containing index, source, relevance %, and content
            context_parts.append(
                f"Context {idx} (Source: {source}, Relevance: {score*100:.0f}%):\n{content}"
            )
        
        # Join all parts with double newlines and return the final single string
        return "\n\n".join(context_parts)
    
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about collections."""
        # Initialize a dictionary structure to hold stats for both collections
        stats = {
            'banking': {
                'total_documents': 0,
                'available': False
            },
            'marketing': {
                'total_documents': 0,
                'available': False
            }
        }
        
        # Check if the banking collection object exists
        if self.banking_collection:
            # Update the count of documents in banking
            stats['banking']['total_documents'] = self.banking_collection.count()
            # Set available flag to True
            stats['banking']['available'] = True
        
        # Check if the marketing collection object exists
        if self.marketing_collection:
            # Update the count of documents in marketing
            stats['marketing']['total_documents'] = self.marketing_collection.count()
            # Set available flag to True
            stats['marketing']['available'] = True
        
        # Return the populated statistics dictionary
        return stats


class FinancialRetriever:
    """
    Simplified retriever specifically for ICICI HFC documents.
    Compatible with validate.py script.
    
    FIXED: Removed embedding_function parameter when getting existing collection
    """
    
    def __init__(self):
        """Initialize retriever with banking collection."""
        # Print initialization message
        print("🔍 Initializing Financial Retriever...")
        
        # Create a persistent ChromaDB client connection
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        
        # Load the embedding model (useful if manual encoding is needed later)
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # FIX: Get collection WITHOUT embedding_function parameter
        # The collection already has its embedding function stored in the DB configuration
        try:
            # Attempt to retrieve the banking collection
            self.collection = self.client.get_collection(name=BANKING_COLLECTION)
            # Print success message with chunk count
            print(f"Collection loaded: {self.collection.count()} chunks")
        # Handle failures in loading the collection
        except Exception as e:
            # Print error message
            print(f"Error loading collection: {e}")
            # Re-raise the exception to stop execution since this class relies entirely on this collection
            raise
    
    
    def retrieve(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None):
        """
        Retrieve documents matching the query.
        
        Args:
            query (str): Search query
            n_results (int): Number of results to return
            filter_metadata (Dict): Optional metadata filters
            
        Returns:
            Dict with 'documents', 'metadatas', 'distances', 'ids'
        """
        # Start try block to handle query execution
        try:
            # Execute query against the collection
            results = self.collection.query(
                query_texts=[query],      # The text to search for
                n_results=n_results,      # Number of matches
                where=filter_metadata     # Filters
            )
            # Return the raw results dictionary from ChromaDB
            return results
        # Catch any exceptions during retrieval
        except Exception as e:
            # Print error message
            print(f"Error during retrieval: {e}")
            # Return a structurally correct but empty dictionary to prevent downstream crashes
            return {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]],
                'ids': [[]]
            }


def main():
    """Demo: Test retriever functionality."""
    # Print header for Demo Mode
    print("Knowledge Retriever - Demo Mode\n")
    
    # Instantiate the KnowledgeRetriever class
    retriever = KnowledgeRetriever()
    
    # Fetch statistics for the collections
    stats = retriever.get_collection_stats()
    # Print the stats header
    print("\nCollection Statistics:")
    # Print banking stats
    print(f"Banking: {stats['banking']['total_documents']} documents")
    # Print marketing stats
    print(f"Marketing: {stats['marketing']['total_documents']} documents")
    
    # Check if banking documents exist to proceed with testing
    if stats['banking']['total_documents'] > 0:
        # Print separator
        print("\n" + "="*60)
        # Print test section header
        print("Testing Banking Search")
        # Print separator
        print("="*60)
        
        # Define a test query string
        test_query = "home loan interest rate"
        # Print the query being tested
        print(f"\nQuery: '{test_query}'\n")
        
        # Perform a search on the banking collection with limit 3
        results = retriever.search_banking(test_query, n_results=3)
        
        # Check if any results were returned
        if results:
            # Loop through results with index
            for idx, result in enumerate(results, start=1):
                # Print result number
                print(f"\n--- Result {idx} ---")
                # Print similarity score as percentage
                print(f"Similarity: {result['similarity_score']*100:.1f}%")
                # Print source filename from metadata
                print(f"Source: {result['metadata'].get('source', 'unknown')}")
                # Print the first 200 characters of the content
                print(f"Content: {result['content'][:200]}...")
        else:
            # Print message if list is empty
            print("No results found.")
        
        # Print separator
        print("\n" + "="*60)
        # Print context formatting test header
        print("Testing Context Formatting for Agents")
        # Print separator
        print("="*60)
        
        # Generate the formatted context string used for LLMs
        context = retriever.get_context_for_agent(test_query, n_results=2)
        # Print the resulting context string
        print(f"\n{context}")
    
    else:
        # If no documents exist, print warning
        print("\n No documents in collections yet.")
        # Print next steps instructions
        print(" Next steps:")
        # Instruction 1
        print("1. Run index_icici_docs.py to index documents")
        # Instruction 2
        print("2. Re-run this retriever demo to test searches")


# Standard boilerplate to run main() only if executed directly
if __name__ == "__main__":
    main()