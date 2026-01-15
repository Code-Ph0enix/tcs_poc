"""
RAG Agent: Combines ChromaDB retrieval with LLM generation
Location: second/agents/rag_agent.py

No direct file output

Note: Queries ChromaDB and prints results to console
"""

from groq import Groq
# Add after line 6 (after warnings import)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Then keep existing imports:
from groq import Groq
from vectorstore.retriever import FinancialRetriever
from config import GROQ_API_KEY, GROQ_MODEL, BANKING_AGENT_TEMPERATURE

import warnings

warnings.filterwarnings('ignore')


class KnowledgeAgent:
    """RAG Agent for ICICI HFC Home Loan queries"""
    
    def __init__(self):
        """Initialize RAG components"""
        print(" Initializing RAG Agent...")
        
        # Initialize retriever
        self.retriever = FinancialRetriever()
        print(f" Retriever loaded: {self.retriever.collection.count()} chunks")
        
        # Initialize Groq client
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        self.temperature = BANKING_AGENT_TEMPERATURE
        
        print(f" LLM initialized: {GROQ_MODEL}")
        print(" RAG Agent ready!\n")
    
    
    def format_context(self, retrieval_results):
        """Format retrieved chunks into context string"""
        contexts = []
        
        for idx, (doc, metadata) in enumerate(zip(
            retrieval_results['documents'][0],
            retrieval_results['metadatas'][0]
        ), 1):
            source = metadata.get('source', 'Unknown')
            doc_type = metadata.get('doc_type', 'general')
            loan_type = metadata.get('loan_type', 'general')
            
            contexts.append(
                f"[Source {idx}: {source} - {doc_type}/{loan_type}]\n{doc}\n"
            )
        
        return "\n---\n".join(contexts)
    
    
    def generate_answer(self, question, context):
        """Generate answer using Groq LLM"""
        
        prompt = f"""You are an expert ICICI Home Finance customer service assistant. Answer the user's question based ONLY on the provided context.

**CONTEXT FROM ICICI HFC DOCUMENTS:**
{context}

**USER QUESTION:**
{question}

**INSTRUCTIONS:**
1. Answer the question accurately using ONLY the information from the context above
2. If the context doesn't contain enough information, say "I don't have specific information about that in the ICICI HFC documents"
3. Be specific with numbers, rates, and requirements when available
4. Format your answer in a clear, structured way
5. If mentioning documents required, list them as bullet points
6. Always mention this is for ICICI Home Finance Corporation (ICICI HFC)

**ANSWER:**"""

        # Call Groq API
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert ICICI Home Finance customer service assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=self.model,
            temperature=self.temperature,
            max_tokens=1024
        )
        
        return chat_completion.choices[0].message.content
    
    
    def query(self, question, n_results=3, filters=None, return_sources=True):
        """
        Execute RAG query
        
        Args:
            question: User's question
            n_results: Number of chunks to retrieve
            filters: Optional metadata filters (dict)
            return_sources: Whether to return source documents
            
        Returns:
            dict with answer and optional sources
        """
        #  FIX: Use correct parameter name 'filter_metadata'
        retrieval_results = self.retriever.retrieve(
            query=question,
            n_results=n_results,
            filter_metadata=filters  #  CORRECT PARAMETER NAME
        )
        
        if not retrieval_results['documents'][0]:
            return {
                'answer': "I couldn't find any relevant information in the ICICI HFC documents.",
                'sources': []
            }
        
        # Step 2: Format context
        context = self.format_context(retrieval_results)
        
        # Step 3: Generate answer with LLM
        answer = self.generate_answer(question, context)
        
        # Prepare response
        response = {'answer': answer}
        
        if return_sources:
            sources = []
            for doc, meta, dist in zip(
                retrieval_results['documents'][0],
                retrieval_results['metadatas'][0],
                retrieval_results['distances'][0]
            ):
                sources.append({
                    'source': meta.get('source', 'Unknown'),
                    'doc_type': meta.get('doc_type', 'general'),
                    'loan_type': meta.get('loan_type', 'general'),
                    'relevance': round((1 - dist) * 100, 2),
                    'preview': doc[:200] + "..."
                })
            
            response['sources'] = sources
        
        return response


if __name__ == "__main__":
    # Quick test
    agent = KnowledgeAgent()
    result = agent.query("What documents are needed for salaried home loan?")
    print("\n ANSWER:")
    print(result['answer'])
    print("\n SOURCES:")
    for i, src in enumerate(result['sources'], 1):
        print(f"{i}. {src['source']} ({src['relevance']}%)")