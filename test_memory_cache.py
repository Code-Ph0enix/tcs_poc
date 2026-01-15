"""
Test Memory and Cache System
Location: second/test_memory_cache.py

SAVES IT TO:
Folders: ./memory/ and ./cache/
Files:
Memory: {session_id}.json
Cache: response_cache.json
"""

from agents.supervisor_agent import SupervisorAgent
import time


def test_memory_system():
    """Test conversation memory"""
    print("\n" + "="*70)
    print("TEST 1: CONVERSATION MEMORY")
    print("="*70)
    
    supervisor = SupervisorAgent(enable_memory=True, enable_cache=False)
    
    session_id = "test_session_001"
    
    # Query 1
    print("\n📝 Query 1: What documents needed for home loan?")
    result1 = supervisor.route_query(
        "What documents are needed for home loan?",
        session_id=session_id
    )
    print(f" Answer: {result1['answer'][:150]}...")
    
    # Query 2 (follow-up, needs context)
    print("\n📝 Query 2: What about self-employed?")
    result2 = supervisor.route_query(
        "What about self-employed?",
        session_id=session_id
    )
    print(f" Answer: {result2['answer'][:150]}...")
    
    # Check memory
    history = supervisor.memory.get_history(session_id)
    print(f"\n💾 Memory: {len(history)} exchanges stored")
    
    for i, exchange in enumerate(history, 1):
        print(f"\n  Exchange {i}:")
        print(f"    User: {exchange['user']}")
        print(f"    Agent: {exchange['agent'][:80]}...")


def test_cache_system():
    """Test response caching"""
    print("\n\n" + "="*70)
    print("TEST 2: RESPONSE CACHING")
    print("="*70)
    
    supervisor = SupervisorAgent(enable_memory=False, enable_cache=True)
    
    query = "What is the eligibility for home loan?"
    
    # First call - should hit LLM
    print(f"\n📝 First call: {query}")
    start = time.time()
    result1 = supervisor.route_query(query)
    time1 = time.time() - start
    print(f"⏱️ Time: {time1:.2f}s")
    print(f" Answer: {result1['answer'][:100]}...")
    
    # Second call - should hit cache
    print(f"\n📝 Second call (same query): {query}")
    start = time.time()
    result2 = supervisor.route_query(query)
    time2 = time.time() - start
    print(f"⏱️ Time: {time2:.2f}s (should be faster!)")
    print(f" Answer: {result2['answer'][:100]}...")
    
    speedup = time1 / time2 if time2 > 0 else 0
    print(f"\n🚀 Speedup: {speedup:.1f}x faster with cache!")
    
    # Cache stats
    stats = supervisor.cache.get_stats()
    print(f"\n Cache Stats:")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   By agent: {stats['by_agent']}")


def test_combined():
    """Test memory + cache together"""
    print("\n\n" + "="*70)
    print("TEST 3: MEMORY + CACHE COMBINED")
    print("="*70)
    
    supervisor = SupervisorAgent(enable_memory=True, enable_cache=True)
    
    session_id = "combined_test"
    
    queries = [
        "What is home loan eligibility?",
        "Create a social media campaign for young professionals",
        "What is home loan eligibility?",  # Should hit cache
        "What documents are needed?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}/{len(queries)}: {query}")
        print(f"{'='*70}")
        
        result = supervisor.route_query(query, session_id=session_id)
        
        from_cache = result.get('from_cache', False)
        print(f"Agent: {result['agent']} {'(CACHED)' if from_cache else ''}")
        print(f"Answer: {result['answer'][:120]}...")
    
    # Final stats
    print(f"\n\n{'='*70}")
    print("FINAL STATS:")
    print(f"{'='*70}")
    print(f"Memory: {len(supervisor.memory.get_history(session_id))} exchanges")
    print(f"Cache: {supervisor.cache.get_stats()['total_entries']} entries")


if __name__ == "__main__":
    print("🧪 TESTING MEMORY & CACHE SYSTEM")
    print("="*70)
    
    test_memory_system()
    test_cache_system()
    test_combined()
    
    print("\n\n" + "="*70)
    print(" ALL MEMORY & CACHE TESTS COMPLETE!")
    print("="*70)
