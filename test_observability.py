"""
Test Observability & Feedback System
Location: tcs_poc/test_observability.py

SAVES IT TO:
Folders: ./logs/ and ./feedback/
Files:
Logs: queries_YYYYMMDD.jsonl, metrics_*.json
Feedback: feedbacks.jsonl, report_*.json
"""

from agents.supervisor_agent import SupervisorAgent
import time


def test_observability():
    """Test LangSmith + Performance Monitoring"""
    print("\n" + "="*70)
    print("TEST 1: OBSERVABILITY & LANGSMITH TRACING")
    print("="*70)
    
    supervisor = SupervisorAgent(
        enable_memory=True,
        enable_cache=True,
        enable_monitoring=True,
        enable_feedback=True
    )
    
    # Test queries
    test_queries = [
        "What documents are needed for home loan?",
        "Create email campaign for young professionals",
        "What is the eligibility criteria?",
        "Generate social media post about top-up loans"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}/{len(test_queries)}: {query}")
        print(f"{'='*70}")
        
        result = supervisor.route_query(query, session_id="obs_test")
        
        print(f"\nAgent: {result['agent']}")
        print(f"Response: {result['answer'][:150]}...")
        
        time.sleep(0.5)  # Small delay
    
    # Get performance stats
    print(f"\n\n{'='*70}")
    print("PERFORMANCE STATISTICS:")
    print(f"{'='*70}")
    
    stats = supervisor.monitor.get_stats()
    print(f"Total queries: {stats['total_queries']}")
    print(f"Success rate: {stats['success_rate']}%")
    print(f"Avg response time: {stats['avg_response_time']}s")
    print(f"\nBy Agent:")
    for agent, data in stats['by_agent'].items():
        print(f"  {agent}: {data['count']} queries, {data['avg_time']}s avg")
    
    # Check for anomalies
    anomalies = supervisor.monitor.detect_anomalies()
    if anomalies:
        print(f"\n⚠️ Anomalies detected: {len(anomalies)}")
        for anomaly in anomalies[:3]:
            print(f"  - {anomaly['type']}: {anomaly.get('query', 'N/A')}")
    
    # Export metrics
    supervisor.monitor.export_metrics()


def test_feedback_system():
    """Test user feedback collection"""
    print("\n\n" + "="*70)
    print("TEST 2: FEEDBACK SYSTEM")
    print("="*70)
    
    supervisor = SupervisorAgent(
        enable_memory=False,
        enable_cache=False,
        enable_monitoring=False,
        enable_feedback=True
    )
    
    # Simulate user interactions with feedback
    interactions = [
        {
            'query': "What is home loan eligibility?",
            'response': "Age 23-60, income 25k+...",
            'rating': 5,
            'comment': "Very clear explanation!",
            'agent': 'knowledge'
        },
        {
            'query': "Create campaign",
            'response': "Subject: Dream home...",
            'rating': 4,
            'comment': "Good but could be more creative",
            'agent': 'marketing'
        },
        {
            'query': "Documents needed?",
            'response': "PAN, Aadhaar...",
            'rating': 5,
            'comment': "Perfect!",
            'agent': 'knowledge'
        },
        {
            'query': "Eligibility for self-employed?",
            'response': "Income proof needed...",
            'rating': 2,
            'comment': "Too generic, need more details",
            'agent': 'knowledge'
        },
        {
            'query': "Generate email",
            'response': "Subject: Own your home...",
            'rating': 3,
            'comment': "Average quality",
            'agent': 'marketing'
        }
    ]
    
    for i, interaction in enumerate(interactions, 1):
        print(f"\nFeedback {i}/{len(interactions)}:")
        print(f"  Query: {interaction['query']}")
        print(f"  Rating: {interaction['rating']}/5")
        
        supervisor.submit_feedback(
            session_id=f"user_{i}",
            query=interaction['query'],
            response=interaction['response'],
            rating=interaction['rating'],
            comment=interaction['comment'],
            agent_type=interaction['agent']
        )
    
    # Get feedback stats
    print(f"\n\n{'='*70}")
    print("FEEDBACK STATISTICS:")
    print(f"{'='*70}")
    
    stats = supervisor.feedback.get_feedback_stats()
    print(f"Total feedbacks: {stats['total_feedbacks']}")
    print(f"Average rating: {stats['avg_rating']}/5")
    print(f"Satisfaction rate: {stats['satisfaction_rate']}%")
    print(f"👍 Thumbs up: {stats['thumbs_up']}")
    print(f"👎 Thumbs down: {stats['thumbs_down']}")
    
    print(f"\nBy Agent:")
    for agent, data in stats['by_agent'].items():
        print(f"  {agent}: {data['count']} feedbacks, {data['avg_rating']}/5 avg")
    
    # Show negative feedback for improvement
    print(f"\n\n{'='*70}")
    print("AREAS FOR IMPROVEMENT (Negative Feedback):")
    print(f"{'='*70}")
    
    negative = supervisor.feedback.get_negative_feedback(3)
    for fb in negative:
        print(f"\n❌ Query: {fb['query']}")
        print(f"   Rating: {fb['rating']}/5")
        print(f"   Comment: {fb['comment']}")
        print(f"   Agent: {fb['agent_type']}")
    
    # Export report
    supervisor.feedback.export_feedback_report()


def test_complete_flow():
    """Test complete flow with all features"""
    print("\n\n" + "="*70)
    print("TEST 3: COMPLETE FLOW (Memory + Cache + Monitoring + Feedback)")
    print("="*70)
    
    supervisor = SupervisorAgent(
        enable_memory=True,
        enable_cache=True,
        enable_monitoring=True,
        enable_feedback=True
    )
    
    session_id = "complete_test_with_observability"
    
    # Query 1
    print(f"\n{'#'*70}")
    print("Step 1: User asks question")
    print(f"{'#'*70}")
    
    result1 = supervisor.route_query(
        "What documents are needed for salaried home loan?",
        session_id=session_id
    )
    print(f" Answer: {result1['answer'][:120]}...")
    
    # Feedback 1
    print("\nStep 2: User gives positive feedback")
    supervisor.submit_feedback(
        session_id=session_id,
        query="What documents are needed for salaried home loan?",
        response=result1['answer'],
        rating=5,
        comment="Exactly what I needed!",
        agent_type=result1['agent']
    )
    
    # Query 2 (should use cache)
    print(f"\n{'#'*70}")
    print("Step 3: Same query (should hit cache)")
    print(f"{'#'*70}")
    
    result2 = supervisor.route_query(
        "What documents are needed for salaried home loan?",
        session_id=session_id
    )
    
    # Query 3 (marketing)
    print(f"\n{'#'*70}")
    print("Step 4: Marketing query")
    print(f"{'#'*70}")
    
    result3 = supervisor.route_query(
        "Create a social media campaign for home loans",
        session_id=session_id
    )
    print(f" Campaign: {result3['answer'][:120]}...")
    
    # Feedback 3
    print("\nStep 5: User gives negative feedback on campaign")
    supervisor.submit_feedback(
        session_id=session_id,
        query="Create a social media campaign for home loans",
        response=result3['answer'],
        rating=2,
        comment="Not creative enough",
        agent_type=result3['agent']
    )
    
    # Final summary
    print(f"\n\n{'='*70}")
    print("FINAL SUMMARY:")
    print(f"{'='*70}")
    
    print("\n Performance:")
    perf_stats = supervisor.monitor.get_stats()
    print(f"  Queries handled: {perf_stats['total_queries']}")
    print(f"  Success rate: {perf_stats['success_rate']}%")
    print(f"  Avg time: {perf_stats['avg_response_time']}s")
    
    print("\n💾 Memory:")
    history = supervisor.memory.get_history(session_id)
    print(f"  Exchanges stored: {len(history)}")
    
    print("\n🗂️ Cache:")
    cache_stats = supervisor.cache.get_stats()
    print(f"  Entries: {cache_stats['total_entries']}")
    
    print("\n👍 Feedback:")
    feedback_stats = supervisor.feedback.get_feedback_stats()
    print(f"  Total: {feedback_stats['total_feedbacks']}")
    print(f"  Satisfaction: {feedback_stats['satisfaction_rate']}%")
    
    print("\n Check LangSmith dashboard at: https://smith.langchain.com")
    print(f"   Project: {os.getenv('LANGCHAIN_PROJECT', 'agentic-ai-poc-2')}")


if __name__ == "__main__":
    import os
    
    print("🧪 TESTING OBSERVABILITY & FEEDBACK SYSTEM")
    print("="*70)
    
    test_observability()
    test_feedback_system()
    test_complete_flow()
    
    print("\n\n" + "="*70)
    print(" ALL TESTS COMPLETE!")
    print("="*70)
    print("\n Check outputs:")
    print("  - ./logs/ - Performance logs")
    print("  - ./feedback/ - User feedback")
    print("  - LangSmith: https://smith.langchain.com")
