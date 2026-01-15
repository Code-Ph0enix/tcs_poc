"""
User Feedback System
Location: second/utils/feedback_system.py
Collects and analyzes user feedback

SAVES IT TO:
Folder: ./feedback/
Files:
feedbacks.jsonl (all feedback entries)
report_YYYYMMDD_HHMMSS.json (feedback reports)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import os


class FeedbackCollector:
    """Collects and stores user feedback"""
    
    def __init__(self, feedback_dir: str = "./feedback"):
        """Initialize feedback collector"""
        self.feedback_dir = feedback_dir
        self.feedbacks = []
        
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Load existing feedback
        self._load_feedback()
        
        print(f"👍 Feedback System initialized ({len(self.feedbacks)} existing feedbacks)")
    
    
    def add_feedback(self, session_id: str, query: str, response: str,
                     rating: int, comment: str = "", 
                     agent_type: str = "unknown"):
        """
        Add user feedback
        
        Args:
            session_id: User session ID
            query: Original query
            response: Agent response
            rating: 1 (thumbs down) or 5 (thumbs up)
            comment: Optional text feedback
            agent_type: Which agent responded
        """
        
        feedback = {
            'id': len(self.feedbacks) + 1,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'query': query,
            'response': response[:200],  # Truncate
            'rating': rating,
            'comment': comment,
            'agent_type': agent_type
        }
        
        self.feedbacks.append(feedback)
        
        # Save to file
        self._save_feedback(feedback)
        
        emoji = "👍" if rating >= 4 else "👎"
        print(f"{emoji} Feedback #{feedback['id']}: Rating {rating}/5 | {agent_type}")
        
        return feedback['id']
    
    
    def get_feedback_stats(self) -> Dict:
        """Calculate feedback statistics"""
        if not self.feedbacks:
            return {
                'total_feedbacks': 0,
                'avg_rating': 0,
                'satisfaction_rate': 0
            }
        
        total = len(self.feedbacks)
        ratings = [f['rating'] for f in self.feedbacks]
        avg_rating = sum(ratings) / len(ratings)
        
        # Satisfaction = 4 or 5 stars
        satisfied = sum(1 for r in ratings if r >= 4)
        satisfaction_rate = (satisfied / total) * 100
        
        # By agent type
        by_agent = {}
        for fb in self.feedbacks:
            agent = fb['agent_type']
            if agent not in by_agent:
                by_agent[agent] = {'count': 0, 'ratings': []}
            by_agent[agent]['count'] += 1
            by_agent[agent]['ratings'].append(fb['rating'])
        
        # Calculate averages
        for agent in by_agent:
            ratings = by_agent[agent]['ratings']
            by_agent[agent]['avg_rating'] = round(sum(ratings) / len(ratings), 2)
            del by_agent[agent]['ratings']
        
        return {
            'total_feedbacks': total,
            'avg_rating': round(avg_rating, 2),
            'satisfaction_rate': round(satisfaction_rate, 1),
            'thumbs_up': sum(1 for r in ratings if r >= 4),
            'thumbs_down': sum(1 for r in ratings if r < 4),
            'by_agent': by_agent
        }
    
    
    def get_negative_feedback(self, limit: int = 10) -> List[Dict]:
        """Get recent negative feedback for improvement"""
        negative = [f for f in self.feedbacks if f['rating'] < 4]
        negative.sort(key=lambda x: x['timestamp'], reverse=True)
        return negative[:limit]
    
    
    def get_positive_feedback(self, limit: int = 10) -> List[Dict]:
        """Get recent positive feedback"""
        positive = [f for f in self.feedbacks if f['rating'] >= 4]
        positive.sort(key=lambda x: x['timestamp'], reverse=True)
        return positive[:limit]
    
    
    def export_feedback_report(self, filepath: str = None):
        """Export feedback analysis report"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.feedback_dir, f"report_{timestamp}.json")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'stats': self.get_feedback_stats(),
            'top_negative': self.get_negative_feedback(5),
            'top_positive': self.get_positive_feedback(5)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f" Feedback report exported to: {filepath}")
        return filepath
    
    
    def _save_feedback(self, feedback: Dict):
        """Save individual feedback to file"""
        filepath = os.path.join(self.feedback_dir, "feedbacks.jsonl")
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback) + '\n')
    
    
    def _load_feedback(self):
        """Load existing feedback from file"""
        filepath = os.path.join(self.feedback_dir, "feedbacks.jsonl")
        
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.feedbacks.append(json.loads(line))


if __name__ == "__main__":
    # Test feedback system
    collector = FeedbackCollector()
    
    # Add some feedback
    collector.add_feedback(
        session_id="user_1",
        query="What documents needed?",
        response="You need PAN, Aadhaar...",
        rating=5,
        comment="Very helpful!",
        agent_type="knowledge"
    )
    
    collector.add_feedback(
        session_id="user_2",
        query="Create campaign",
        response="Subject: Dream home...",
        rating=4,
        agent_type="marketing"
    )
    
    collector.add_feedback(
        session_id="user_3",
        query="Eligibility?",
        response="Age 23-60...",
        rating=2,
        comment="Not detailed enough",
        agent_type="knowledge"
    )
    
    # Get stats
    print("\n" + "="*70)
    print("FEEDBACK STATS:")
    print("="*70)
    print(json.dumps(collector.get_feedback_stats(), indent=2))
    
    # Export report
    collector.export_feedback_report()
