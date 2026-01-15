"""
Validation script
Location: second/validate.py
No direct file output

Note: Validation results printed to console only
"""

from vectorstore.retriever import FinancialRetriever
from config import *
import os
import warnings

#  SILENCE TENSORFLOW WARNINGS
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

def run_validation():
    print("=" * 70)
    print("STEP 6 VALIDATION: TESTING CHROMADB RETRIEVAL")
    print("=" * 70)
    
    print("\n🔧 Initializing retriever...")
    
    try:
        retriever = FinancialRetriever()
    except Exception as e:
        print(f"❌ Failed to initialize retriever: {e}")
        print("\n⚠️  Make sure you've run index_icici_docs.py first!")
        return
    
    print(f" Collection loaded: {retriever.collection.count()} chunks")
    
    test_queries = [
        {"query": "What documents are needed for salaried home loan?", "expected_type": "salaried"},
        {"query": "Self-employed eligibility criteria", "expected_type": "self_employed"},
        {"query": "How to apply online for home loan?", "expected_type": "knowledge_hub"},
        {"query": "Balance transfer loan benefits", "expected_type": None},
        {"query": "Plot loan requirements", "expected_type": None}
    ]
    
    print(f"\n🔎 Running {len(test_queries)} test queries...\n")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_queries, 1):
        query = test['query']
        expected = test['expected_type']
        
        print(f"\n[Query {i}] {query}")
        print("-" * 70)
        
        try:
            results = retriever.retrieve(query=query, n_results=2)
            
            if not results['documents'][0]:
                print("  ⚠️  No results found")
                if expected:
                    failed += 1
                continue
            
            for idx, (doc, meta, dist) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                
                relevance = (1 - dist) * 100
                doc_type = meta.get('doc_type', 'unknown')
                loan_type = meta.get('loan_type', 'unknown')
                source = meta.get('source', 'unknown')
                
                print(f"   Match {idx}: {source}")
                print(f"     Type: {doc_type} | Loan: {loan_type} | Relevance: {relevance:.1f}%")
                print(f"     Preview: {doc[:100]}...")
                
                if expected and idx == 1:
                    if doc_type == expected:
                        print(f"      PASS - Correct doc_type")
                        passed += 1
                    else:
                        print(f"     ❌ FAIL - Expected {expected}, got {doc_type}")
                        failed += 1
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            if expected:
                failed += 1
    
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    total_with_expectations = sum(1 for t in test_queries if t['expected_type'])
    if total_with_expectations > 0:
        accuracy = (passed / total_with_expectations) * 100
        print(f" Passed: {passed}/{total_with_expectations}")
        print(f"❌ Failed: {failed}/{total_with_expectations}")
        print(f" Accuracy: {accuracy:.1f}%")
    else:
        print(" All queries executed successfully")
    
    if passed == total_with_expectations:
        print("\n🎉 PERFECT SCORE! All validations passed!")
    elif passed > 0:
        print("\n System is working but could be improved")
    else:
        print("\n⚠️  System needs attention - check your indexing")
    
    print("=" * 70)


if __name__ == "__main__":
    run_validation()