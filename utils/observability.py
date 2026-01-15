"""
Observability & Monitoring System
Location: tcs_poc/utils/observability.py
Tracks agent performance, errors, and metrics

SAVES IT TO:
Folder: ./logs/
Files:
queries_YYYYMMDD.jsonl (daily query logs)
metrics_YYYYMMDD_HHMMSS.json (exported metrics)
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import os
from functools import wraps
from langsmith import traceable


class PerformanceMonitor:
    """Monitors agent performance metrics"""
    
    def __init__(self, log_dir: str = "./logs"):
        """Initialize performance monitor"""
        self.log_dir = log_dir
        self.metrics = []
        
        os.makedirs(log_dir, exist_ok=True)
        
        print(f" Performance Monitor initialized (logs: {log_dir})")
    
    
    def log_query(self, session_id: str, query: str, agent_type: str, 
                  response: str, response_time: float, 
                  success: bool = True, error: Optional[str] = None,
                  metadata: Optional[Dict] = None):
        """Log a query execution"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'query': query,
            'agent_type': agent_type,
            'response_length': len(response),
            'response_time_seconds': round(response_time, 3),
            'success': success,
            'error': error,
            'metadata': metadata or {}
        }
        
        self.metrics.append(log_entry)
        
        # Save to file
        self._save_log(log_entry)
        
        # Print summary
        status = "" if success else "❌"
        print(f"{status} {agent_type.upper()} | {response_time:.2f}s | {query[:50]}...")
    
    
    def get_stats(self) -> Dict:
        """Calculate performance statistics"""
        if not self.metrics:
            return {
                'total_queries': 0,
                'success_rate': 0,
                'avg_response_time': 0
            }
        
        total = len(self.metrics)
        successes = sum(1 for m in self.metrics if m['success'])
        
        # Average response time
        response_times = [m['response_time_seconds'] for m in self.metrics]
        avg_time = sum(response_times) / len(response_times)
        
        # By agent type
        by_agent = {}
        for metric in self.metrics:
            agent = metric['agent_type']
            if agent not in by_agent:
                by_agent[agent] = {'count': 0, 'avg_time': []}
            by_agent[agent]['count'] += 1
            by_agent[agent]['avg_time'].append(metric['response_time_seconds'])
        
        # Calculate averages
        for agent in by_agent:
            times = by_agent[agent]['avg_time']
            by_agent[agent]['avg_time'] = round(sum(times) / len(times), 3)
        
        return {
            'total_queries': total,
            'success_count': successes,
            'error_count': total - successes,
            'success_rate': round((successes / total) * 100, 2),
            'avg_response_time': round(avg_time, 3),
            'by_agent': by_agent
        }
    
    
    def detect_anomalies(self) -> List[Dict]:
        """Detect performance anomalies"""
        if len(self.metrics) < 5:
            return []
        
        # Calculate thresholds
        response_times = [m['response_time_seconds'] for m in self.metrics]
        avg_time = sum(response_times) / len(response_times)
        threshold = avg_time * 2  # 2x slower than average
        
        anomalies = []
        
        for metric in self.metrics[-10:]:  # Check last 10
            # Slow query
            if metric['response_time_seconds'] > threshold:
                anomalies.append({
                    'type': 'slow_query',
                    'query': metric['query'][:50],
                    'time': metric['response_time_seconds'],
                    'threshold': round(threshold, 2)
                })
            
            # Error
            if not metric['success']:
                anomalies.append({
                    'type': 'error',
                    'query': metric['query'][:50],
                    'error': metric['error']
                })
        
        return anomalies
    
    
    def _save_log(self, log_entry: Dict):
        """Save log entry to file"""
        date_str = datetime.now().strftime("%Y%m%d")
        filepath = os.path.join(self.log_dir, f"queries_{date_str}.jsonl")
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    
    def export_metrics(self, filepath: str = None):
        """Export metrics to JSON file"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.log_dir, f"metrics_{timestamp}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'stats': self.get_stats(),
                'anomalies': self.detect_anomalies(),
                'recent_queries': self.metrics[-20:]
            }, f, indent=2)
        
        print(f"📁 Metrics exported to: {filepath}")
        return filepath


def track_performance(monitor: PerformanceMonitor):
    """Decorator to track function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            response = None
            
            try:
                response = func(*args, **kwargs)
                return response
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                response_time = time.time() - start_time
                
                # Extract query from args/kwargs
                query = kwargs.get('query', '') or (args[1] if len(args) > 1 else '')
                
                if response:
                    monitor.log_query(
                        session_id=kwargs.get('session_id', 'default'),
                        query=str(query),
                        agent_type=response.get('agent', 'unknown'),
                        response=response.get('answer', ''),
                        response_time=response_time,
                        success=success,
                        error=error
                    )
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test monitor
    monitor = PerformanceMonitor()
    
    # Simulate some queries
    monitor.log_query(
        session_id="test_1",
        query="What is home loan eligibility?",
        agent_type="knowledge",
        response="Eligibility includes age 23-60...",
        response_time=1.2,
        success=True
    )
    
    monitor.log_query(
        session_id="test_1",
        query="Create email campaign",
        agent_type="marketing",
        response="Subject: Dream home awaits...",
        response_time=2.5,
        success=True
    )
    
    # Get stats
    print("\n" + "="*70)
    print("PERFORMANCE STATS:")
    print("="*70)
    print(json.dumps(monitor.get_stats(), indent=2))
    
    # Export
    monitor.export_metrics()
