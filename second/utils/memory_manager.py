"""
Conversation Memory Manager
Location: second/utils/memory_manager.py
Manages conversation history per session
SAVES IT TO:
Folder: ./memory/
File: {session_id}.json (one file per session)
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class ConversationMemory:
    """Manages conversation history with sliding window"""
    
    def __init__(self, max_history: int = 10, persist_dir: str = "./memory"):
        """
        Initialize conversation memory
        
        Args:
            max_history: Maximum number of exchanges to remember
            persist_dir: Directory to save conversation history
        """
        self.max_history = max_history
        self.persist_dir = persist_dir
        self.sessions = {}  # session_id -> conversation history
        
        # Create persistence directory
        os.makedirs(persist_dir, exist_ok=True)
        
        print(f"💾 Memory Manager initialized (max history: {max_history})")
    
    
    def add_exchange(self, session_id: str, user_query: str, agent_response: str, 
                     agent_type: str = "knowledge", metadata: Optional[Dict] = None):
        """Add a user-agent exchange to memory"""
        
        # Initialize session if new
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        # Create exchange record
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user': user_query,
            'agent': agent_response,
            'agent_type': agent_type,
            'metadata': metadata or {}
        }
        
        # Add to session history
        self.sessions[session_id].append(exchange)
        
        # Trim to max history (sliding window)
        if len(self.sessions[session_id]) > self.max_history:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history:]
        
        # Auto-persist
        self._save_session(session_id)
    
    
    def get_history(self, session_id: str, last_n: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            last_n: Number of recent exchanges to return (None = all)
        """
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id]
        
        if last_n:
            return history[-last_n:]
        return history
    
    
    def get_context_string(self, session_id: str, last_n: int = 5) -> str:
        """Get formatted conversation history as context string"""
        history = self.get_history(session_id, last_n)
        
        if not history:
            return "No previous conversation history."
        
        context_parts = ["Previous conversation:"]
        for i, exchange in enumerate(history, 1):
            context_parts.append(f"\nUser: {exchange['user']}")
            context_parts.append(f"Assistant: {exchange['agent'][:200]}...")  # Truncate
        
        return "\n".join(context_parts)
    
    
    def clear_session(self, session_id: str):
        """Clear history for a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            # Delete persisted file
            filepath = os.path.join(self.persist_dir, f"{session_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            
            print(f"🗑️ Cleared session: {session_id}")
    
    
    def _save_session(self, session_id: str):
        """Persist session to disk"""
        filepath = os.path.join(self.persist_dir, f"{session_id}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.sessions[session_id], f, indent=2, ensure_ascii=False)
    
    
    def load_session(self, session_id: str) -> bool:
        """Load session from disk"""
        filepath = os.path.join(self.persist_dir, f"{session_id}.json")
        
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            self.sessions[session_id] = json.load(f)
        
        print(f"📂 Loaded session: {session_id} ({len(self.sessions[session_id])} exchanges)")
        return True
    
    
    def list_sessions(self) -> List[str]:
        """List all persisted sessions"""
        if not os.path.exists(self.persist_dir):
            return []
        
        files = os.listdir(self.persist_dir)
        sessions = [f.replace('.json', '') for f in files if f.endswith('.json')]
        return sessions


if __name__ == "__main__":
    # Test memory manager
    memory = ConversationMemory(max_history=5)
    
    # Simulate conversation
    session_id = "user_123"
    
    memory.add_exchange(
        session_id=session_id,
        user_query="What documents are needed for home loan?",
        agent_response="You need PAN card, Aadhaar, salary slips...",
        agent_type="knowledge"
    )
    
    memory.add_exchange(
        session_id=session_id,
        user_query="What about eligibility?",
        agent_response="Age 23-60, minimum income 25k...",
        agent_type="knowledge"
    )
    
    # Get history
    print("\n" + "="*70)
    print("CONVERSATION HISTORY:")
    print("="*70)
    print(memory.get_context_string(session_id))
    
    print(f"\n Session saved to: ./memory/{session_id}.json")
