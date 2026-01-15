"""
Supervisor Agent - Routes queries to appropriate specialized agent
Location: second/agents/supervisor_agent.py

SAVES IT TO:
Folders: ./cache/, ./memory/, ./logs/, ./feedback/
Note: Uses all utility systems depending on enabled flags
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
from agents.knowledge_agent import KnowledgeAgent
from agents.marketing_agent import MarketingAgent
from utils.memory_manager import ConversationMemory
from utils.cache_manager import ResponseCache
from utils.observability import PerformanceMonitor
from utils.feedback_system import FeedbackCollector
from langsmith import traceable
import warnings
import time

warnings.filterwarnings('ignore')


class SupervisorAgent:
    """Supervisor that routes queries to specialized agents"""
    
    def __init__(self, enable_memory: bool = True, enable_cache: bool = True,
                 enable_monitoring: bool = True, enable_feedback: bool = True):
        """Initialize supervisor and all sub-agents"""
        print(" Initializing Supervisor Agent...")
        
        # Initialize LLM for routing decisions
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        
        # Initialize memory and cache
        self.enable_memory = enable_memory
        self.enable_cache = enable_cache
        
        if enable_memory:
            self.memory = ConversationMemory(max_history=10)
            print(" Memory enabled (10 exchanges)")
        
        if enable_cache:
            self.cache = ResponseCache(ttl_hours=24)
            print(" Cache enabled (24h TTL)")
        
        # Initialize monitoring and feedback
        self.enable_monitoring = enable_monitoring
        self.enable_feedback = enable_feedback
        
        if enable_monitoring:
            self.monitor = PerformanceMonitor()
            print(" Performance monitoring enabled")
        
        if enable_feedback:
            self.feedback = FeedbackCollector()
            print(" Feedback system enabled")
        
        # Initialize specialized agents
        print("\n Loading Knowledge Agent...")
        self.knowledge_agent = KnowledgeAgent()
        
        print("\n Loading Marketing Agent...")
        self.marketing_agent = MarketingAgent()
        
        print("\n Supervisor Agent ready with 2 specialized agents!\n")
    
    
    def classify_query(self, query):
        """
        Classify user query to route to correct agent
        
        Returns: 'knowledge' or 'marketing'
        """
        prompt = f"""You are a query classifier for a banking AI system.

**USER QUERY:** {query}

**TASK:** Classify this query into ONE of these categories:

1. **knowledge** - User wants information about:
   - Product features, eligibility, documents required
   - How to apply, loan process
   - Interest rates, fees, terms
   - Answering questions about banking products

2. **marketing** - User wants to:
   - Generate marketing campaigns
   - Create promotional content
   - Write social media posts, emails, SMS
   - Design marketing materials

**RESPOND WITH ONLY ONE WORD:** knowledge OR marketing

**CLASSIFICATION:**"""

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a query classifier."},
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            temperature=0.1,
            max_tokens=10
        )
        
        classification = response.choices[0].message.content.strip().lower()
        
        # Default to knowledge if unclear
        if 'marketing' in classification:
            return 'marketing'
        else:
            return 'knowledge'
    
    
    @traceable(name="route_query", tags=["supervisor", "routing"])
    def route_query(self, query: str, session_id: str = "default", 
                    n_results: int = 3, filters=None):
        """
        Route query to appropriate agent with full observability
        """
        start_time = time.time()
        success = True
        error_msg = None
        result = {}
        
        try:
            # Check cache first
            if self.enable_cache:
                cached_response = self.cache.get(query, agent_type="any")
                if cached_response:
                    return {
                        'agent': 'cached',
                        'response_type': 'cached',
                        'answer': cached_response,
                        'from_cache': True
                    }
            
            # Get conversation context if memory enabled
            context = ""
            if self.enable_memory:
                context = self.memory.get_context_string(session_id, last_n=3)
            
            # Classify the query
            agent_type = self.classify_query(query)
            
            print(f"\n Routing to: {agent_type.upper()} Agent")
            print("="*70)
            
            if agent_type == 'marketing':
                # Extract campaign parameters
                campaign_type = 'social_media'
                target_audience = 'salaried'
                
                if 'email' in query.lower():
                    campaign_type = 'email'
                elif 'sms' in query.lower():
                    campaign_type = 'sms'
                elif 'blog' in query.lower():
                    campaign_type = 'blog'
                elif 'poster' in query.lower():
                    campaign_type = 'poster'
                
                if 'self-employed' in query.lower() or 'self employed' in query.lower():
                    target_audience = 'self_employed'
                elif 'young' in query.lower():
                    target_audience = 'young_professionals'
                elif 'family' in query.lower() or 'families' in query.lower():
                    target_audience = 'families'
                
                campaign = self.marketing_agent.generate_campaign(
                    campaign_type=campaign_type,
                    target_audience=target_audience
                )
                
                response = campaign['content']
                
                result = {
                    'agent': 'marketing',
                    'response_type': 'campaign',
                    'campaign': campaign,
                    'answer': response
                }
            
            else:  # knowledge
                result = self.knowledge_agent.query(
                    question=query,
                    n_results=n_results,
                    filters=filters
                )
                
                response = result['answer']
                
                result.update({
                    'agent': 'knowledge',
                    'response_type': 'answer'
                })
            
            # Cache the response
            if self.enable_cache:
                self.cache.set(query, agent_type, response)
            
            # Save to memory
            if self.enable_memory:
                self.memory.add_exchange(
                    session_id=session_id,
                    user_query=query,
                    agent_response=response,
                    agent_type=agent_type
                )
            
            return result
            
        except Exception as e:
            success = False
            error_msg = str(e)
            raise
        
        finally:
            # Log performance
            if self.enable_monitoring:
                response_time = time.time() - start_time
                self.monitor.log_query(
                    session_id=session_id,
                    query=query,
                    agent_type=result.get('agent', 'unknown') if result else 'error',
                    response=result.get('answer', '') if result else '',
                    response_time=response_time,
                    success=success,
                    error=error_msg
                )
    
    
    def submit_feedback(self, session_id: str, query: str, response: str,
                        rating: int, comment: str = "", agent_type: str = "unknown"):
        """Submit user feedback"""
        if self.enable_feedback:
            return self.feedback.add_feedback(
                session_id=session_id,
                query=query,
                response=response,
                rating=rating,
                comment=comment,
                agent_type=agent_type
            )
        return None


if __name__ == "__main__":
    # Test supervisor
    supervisor = SupervisorAgent()
    
    # Test 1: Knowledge query
    print("\n" + "="*70)
    print("TEST 1: Knowledge Query")
    print("="*70)
    result1 = supervisor.route_query("What documents are needed for salaried home loan?")
    print("\n ANSWER:")
    print(result1['answer'][:300] + "...")
    
    # Test 2: Marketing query
    print("\n\n" + "="*70)
    print("TEST 2: Marketing Query")
    print("="*70)
    result2 = supervisor.route_query("Create a social media campaign for home loans targeting salaried professionals")
    print("\n CAMPAIGN:")
    print(result2['answer'][:300] + "...")