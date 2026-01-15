"""
Test Multi-Agent System
Location: tcs_poc/test_multi_agent.py

SAVES IT TO:
Folder: ./cache/ (via SupervisorAgent)
File: response_cache.json
Note: Uses cache from cache_manager when running tests
"""
# saves to cache folder

from agents.supervisor_agent import SupervisorAgent


def test_multi_agent_system():
    """Test the multi-agent orchestration"""
    
    print("\n" + "="*70)
    print("TESTING MULTI-AGENT SYSTEM")
    print("="*70)
    
    # Initialize supervisor
    supervisor = SupervisorAgent()
    
    # Test queries
    test_cases = [
        {
            'query': "What documents are needed for self-employed home loan?",
            'expected_agent': 'knowledge'
        },
        {
            'query': "Create an email campaign for home loans targeting young professionals",
            'expected_agent': 'marketing'
        },
        {
            'query': "What is the eligibility for plot loans?",
            'expected_agent': 'knowledge'
        },
        {
            'query': "Generate a social media post about balance transfer benefits",
            'expected_agent': 'marketing'
        }
    ]
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\n\n{'#'*70}")
        print(f"TEST CASE {idx}/{len(test_cases)}")
        print(f"{'#'*70}")
        print(f"\n📝 Query: {test['query']}")
        print(f"Expected Agent: {test['expected_agent']}")
        
        result = supervisor.route_query(test['query'], n_results=2)
        
        print(f"\n Routed to: {result['agent']} agent")
        print(f"Match: {'✓' if result['agent'] == test['expected_agent'] else '✗'}")
        
        print(f"\n📄 RESPONSE:")
        print("-"*70)
        print(result['answer'][:400] + "..." if len(result['answer']) > 400 else result['answer'])
        
        if result.get('sources'):
            print(f"\n Sources: {len(result['sources'])} documents")
    
    print("\n\n" + "="*70)
    print(" MULTI-AGENT TESTING COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    test_multi_agent_system()
