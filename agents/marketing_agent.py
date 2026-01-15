"""
Marketing Campaign Agent
Location: tcs_poc/agents/marketing_agent.py
Generates marketing campaigns based on banking product data

No direct file output
Note: Generates marketing content, prints to console and saves to ./campaigns/ folder
"""

from groq import Groq
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vectorstore.retriever import FinancialRetriever
from config import GROQ_API_KEY, GROQ_MODEL, BANKING_AGENT_TEMPERATURE
import warnings
import json
from datetime import datetime

warnings.filterwarnings('ignore')

class MarketingAgent:
    """Marketing Campaign Generation Agent for ICICI HFC products"""
    
    def __init__(self):
        """Initialize Marketing Agent"""
        print("Initializing Marketing Campaign Agent...")
        
        # Initialize retriever for product data
        self.retriever = FinancialRetriever()
        print(f" Product knowledge loaded: {self.retriever.collection.count()} chunks")
        
        # Initialize Groq client
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        self.temperature = 0.8  # Higher for creative marketing content
        
        print(f" LLM initialized: {GROQ_MODEL}")
        print(" Marketing Agent ready!\n")
    
    
    def get_product_info(self, product_query, n_results=3):
        """Retrieve product information from knowledge base"""
        results = self.retriever.retrieve(
            query=product_query,
            n_results=n_results
        )
        
        if not results['documents'][0]:
            return None
        
        # Combine retrieved context
        context_parts = []
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            context_parts.append(f"{doc}")
        
        return "\n".join(context_parts)
    
    
    def generate_campaign(self, campaign_type, target_audience, product_type=None):
        """
        Generate marketing campaign
        
        Args:
            campaign_type: email, social_media, sms, poster, blog
            target_audience: salaried, self_employed, young_professionals, families
            product_type: Optional specific product (home_loan, top_up, etc.)
        """
        # Build query for product retrieval
        if product_type:
            query = f"{target_audience} {product_type} features benefits"
        else:
            query = f"{target_audience} home loan"
        
        # Get product information
        product_context = self.get_product_info(query, n_results=3)
        
        if not product_context:
            product_context = "ICICI HFC home loan products with competitive rates and flexible eligibility"
        
        # Generate campaign
        prompt = f"""You are a creative marketing expert for ICICI Home Finance Corporation (ICICI HFC).

**TASK:** Create a {campaign_type} marketing campaign

**TARGET AUDIENCE:** {target_audience}
**PRODUCT INFO:**
{product_context}

**CAMPAIGN REQUIREMENTS:**
1. For {campaign_type} format, create appropriate content
2. Target {target_audience} specifically
3. Highlight key benefits and features from product info
4. Include clear call-to-action
5. Keep tone professional yet engaging
6. Add relevant hashtags if social media
7. Keep within character/word limits for the format

**FORMAT GUIDELINES:**
- Email: Subject + 150-200 word body + CTA
- Social Media: 100-150 words + 3-5 hashtags
- SMS: 160 characters max
- Poster: Headline + 3 key points + tagline
- Blog: Title + 300-400 words with sections

**GENERATE THE CAMPAIGN:**"""

        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative marketing campaign expert for ICICI Home Finance."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=self.model,
            temperature=self.temperature,
            max_tokens=800
        )
        
        campaign_content = response.choices[0].message.content
        
        return {
            'campaign_type': campaign_type,
            'target_audience': target_audience,
            'product_type': product_type or 'home_loan',
            'content': campaign_content,
            'generated_at': datetime.now().isoformat(),
            'status': 'generated'
        }
    
    
    def save_campaign(self, campaign_data, filename=None):
        """Save campaign to file (ACTION)"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"campaign_{campaign_data['campaign_type']}_{timestamp}.txt"
        
        filepath = f"./campaigns/{filename}"
        
        # Create campaigns directory if not exists
        import os
        os.makedirs('./campaigns', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"CAMPAIGN TYPE: {campaign_data['campaign_type']}\n")
            f.write(f"TARGET AUDIENCE: {campaign_data['target_audience']}\n")
            f.write(f"PRODUCT: {campaign_data['product_type']}\n")
            f.write(f"GENERATED: {campaign_data['generated_at']}\n")
            f.write(f"\n{'='*70}\n")
            f.write(f"CAMPAIGN CONTENT:\n")
            f.write(f"{'='*70}\n\n")
            f.write(campaign_data['content'])
        
        print(f" Campaign saved to: {filepath}")
        return filepath


if __name__ == "__main__":
    # Quick test
    agent = MarketingAgent()
    
    campaign = agent.generate_campaign(
        campaign_type="social_media",
        target_audience="salaried",
        product_type="home_loan"
    )
    
    print("\nGENERATED CAMPAIGN:")
    print("="*70)
    print(campaign['content'])
    print("="*70)
    
    # Save it
    agent.save_campaign(campaign)
