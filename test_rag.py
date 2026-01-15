"""
Test RAG Agent
Location: second/test_rag.py
No direct file output

Note: Only prints results to console, retrieves from ChromaDB

"""

from agents.knowledge_agent import KnowledgeAgent


def test_rag_agent():
    """Test RAG agent with sample queries"""
    
    # Initialize agent
    agent = KnowledgeAgent()
    
    # Test queries
    test_queries = [
        "What documents are needed for a salaried person to apply for ICICI home loan?",
        "What is the eligibility criteria for self-employed applicants?",
        "How can I apply for a home loan online at ICICI HFC?",
        "What are the benefits of balance transfer?",
        "Can I get a plot loan? What are the requirements?"
    ]
    
    print("\n" + "=" * 70)
    print("TESTING RAG AGENT WITH SAMPLE QUERIES")
    print("=" * 70)
    
    for idx, query in enumerate(test_queries, 1):
        print(f"\n\n{'#' * 70}")
        print(f"TEST QUERY {idx}/{len(test_queries)}")
        print(f"{'#' * 70}")
        
        result = agent.query(query, n_results=2)
        
        print("\n📝 ANSWER:")
        print("-" * 70)
        print(result['answer'])
        
        print("\n TOP SOURCES:")
        print("-" * 70)
        for i, source in enumerate(result['sources'][:2], 1):
            print(f"{i}. {source['source']} ({source['relevance']}% relevant)")
    
    print("\n\n" + "=" * 70)
    print(" RAG AGENT TESTING COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    test_rag_agent()
