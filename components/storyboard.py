"""
==============================================================================
STORYBOARD COMPONENT - INTERACTIVE AGENT FLOW DEMONSTRATION
==============================================================================

Purpose: This file creates the "Story Demo" tab that shows how the multi-agent
         system works through pre-scripted scenarios. It's like a guided tour
         that demonstrates:
         - How queries flow through the system
         - How the supervisor routes to different agents
         - How memory, cache, and observability work together
         - Visual agent activation and data flow

Location: second/components/storyboard.py

Called by: streamlit_app.py when "Story Demo" tab is selected

Think of this as a "movie" showing how your AI system works internally.
Users can play, pause, and step through different scenarios.

==============================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import streamlit as st  # For creating web UI
import time  # For delays and timestamps
from typing import Dict, List, Any  # For type hints
import json  # For displaying data structures

# ==============================================================================
# STORY SCENARIOS DATABASE
# ==============================================================================
# These are pre-written stories that demonstrate different use cases

STORY_SCENARIOS = {
    # Dictionary where each key is a scenario name, value is scenario details
    
    "knowledge_query": {
        # Scenario 1: Knowledge Agent workflow
        
        "title": "📚 Story 1: Priya Asks About Home Loan Documents",
        # Title shown to user
        
        "description": """
            Priya is a 28-year-old salaried professional looking to buy her first home.
            She wants to know what documents she needs to apply for a home loan.
            Watch how the AI system processes her query step-by-step.
        """,
        # Background story (context for the user)
        
        "persona": {
            # Character details for storytelling
            "name": "Priya",
            "age": 28,
            "occupation": "Software Engineer",
            "goal": "Buy first home"
        },
        
        "query": "What documents do I need for a salaried home loan at ICICI?",
        # The question Priya will ask
        
        "expected_agent": "knowledge",
        # Which agent should handle this (for demonstration)
        
        "steps": [
            # List of dictionaries, each representing one step in the story
            # The story unfolds step-by-step
            
            {
                "step_number": 1,
                "title": "📝 Step 1: User Query Received",
                "description": "Priya types her question into the system",
                "active_component": "user",  # Which part is "active" (for highlighting)
                "details": "Query: 'What documents do I need for a salaried home loan at ICICI?'",
                "code_snippet": "query = user_input.get_text()",  # Simulated code
                "duration": 0.5  # How long to show this step (seconds)
            },
            
            {
                "step_number": 2,
                "title": "🤖 Step 2: Supervisor Agent - Query Classification",
                "description": "The Supervisor Agent analyzes the query to determine which specialized agent should handle it",
                "active_component": "supervisor",
                "details": """
                    The supervisor uses an LLM to classify the query type:
                    - Is it asking for information? → Knowledge Agent
                    - Is it requesting marketing content? → Marketing Agent
                    
                    Analysis: This query is asking about 'documents' and 'eligibility'.
                    Classification: KNOWLEDGE query
                    Decision: Route to Knowledge Agent ✓
                """,
                "code_snippet": """
# Supervisor classification logic
def classify_query(query):
    prompt = f"Classify this query: {query}"
    classification = llm.generate(prompt)
    if 'knowledge' in classification:
        return 'knowledge_agent'
                """,
                "duration": 1.5
            },
            
            {
                "step_number": 3,
                "title": "💾 Step 3: Cache Check",
                "description": "Before doing expensive LLM calls, check if we've seen this exact question before",
                "active_component": "cache",
                "details": """
                    Cache Manager checks for identical previous queries:
                    - Generates hash of query: md5('what documents...')
                    - Looks up in cache: ./cache/response_cache.json
                    
                    Result: ❌ CACHE MISS (first time asking this question)
                    Action: Proceed to Knowledge Agent for full processing
                    
                    If this was a cache hit, we could return answer in ~0.1s!
                """,
                "code_snippet": """
# Cache lookup
cache_key = hash_query(query)
cached_response = cache.get(cache_key)
if cached_response:
    return cached_response  # Instant!
else:
    # Continue to agent...
                """,
                "duration": 1.0
            },
            
            {
                "step_number": 4,
                "title": "📚 Step 4: Knowledge Agent - Document Retrieval",
                "description": "The Knowledge Agent searches the vector database for relevant information",
                "active_component": "knowledge_agent",
                "details": """
                    RAG Pipeline Step 1: RETRIEVAL
                    
                    1. Convert query to embedding vector (384 dimensions)
                    2. Search ChromaDB using cosine similarity
                    3. Find top 3 most relevant document chunks
                    
                    Retrieved Documents:
                    ✓ salaried.txt (Chunk 2) - Relevance: 94.3%
                    ✓ salaried.txt (Chunk 5) - Relevance: 89.7%
                    ✓ knowledge_hub.txt (Chunk 12) - Relevance: 85.2%
                    
                    These chunks contain specific information about documents
                    required for salaried applicants.
                """,
                "code_snippet": """
# Vector search in ChromaDB
query_embedding = model.encode(query)
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)
                """,
                "duration": 2.0
            },
            
            {
                "step_number": 5,
                "title": "🧠 Step 5: Knowledge Agent - LLM Generation",
                "description": "Combine retrieved documents with the query and send to LLM for answer generation",
                "active_component": "knowledge_agent",
                "details": """
                    RAG Pipeline Step 2: AUGMENTED GENERATION
                    
                    1. Format retrieved chunks as context
                    2. Create prompt: "Based on these documents, answer..."
                    3. Send to Groq LLM (llama-3.1-70b-versatile)
                    4. LLM generates answer using ONLY the provided context
                    
                    Context Size: ~1,200 tokens
                    LLM Response Time: 1.8 seconds
                    
                    Generated Answer: "For ICICI HFC salaried home loan, you need:
                    - PAN Card, Aadhaar Card
                    - Last 3 months salary slips
                    - Last 6 months bank statements
                    - Form 16 or IT returns for last 2 years
                    - Property documents..."
                """,
                "code_snippet": """
# LLM generation with context
context = format_retrieved_docs(results)
prompt = f'''
Context: {context}
Question: {query}
Answer based only on context:
'''
answer = llm.generate(prompt)
                """,
                "duration": 2.5
            },
            
            {
                "step_number": 6,
                "title": "💾 Step 6: Save to Cache",
                "description": "Store the answer in cache for instant retrieval if same question is asked again",
                "active_component": "cache",
                "details": """
                    Cache Storage:
                    - File: ./cache/response_cache.json
                    - Key: md5(query + agent_type)
                    - Value: Generated answer + metadata
                    - TTL: 24 hours (expires after 1 day)
                    
                    Next time this exact query is asked:
                    Response time: 0.1s instead of 4.3s
                    Cost savings: Skip LLM API call
                    
                    Cache entry saved successfully ✓
                """,
                "code_snippet": """
# Save to cache
cache.set(
    query=query,
    agent_type='knowledge',
    response=answer,
    ttl_hours=24
)
                """,
                "duration": 0.8
            },
            
            {
                "step_number": 7,
                "title": "📊 Step 7: Log to Observability",
                "description": "Record performance metrics for monitoring and analytics",
                "active_component": "observability",
                "details": """
                    Performance Monitor logs this query:
                    
                    Metrics Recorded:
                    - Query: "What documents..."
                    - Agent: knowledge
                    - Response Time: 4.3 seconds
                    - Success: True
                    - Timestamp: 2026-01-15 12:22:45
                    - Session ID: session_1736920965
                    
                    Saved to: ./logs/queries_20260115.jsonl
                    
                    This data is used for:
                    - Performance tracking
                    - Anomaly detection (queries > 5s)
                    - Analytics dashboard
                """,
                "code_snippet": """
# Performance logging
monitor.log_query(
    query=query,
    agent_type='knowledge',
    response_time=4.3,
    success=True
)
                """,
                "duration": 0.5
            },
            
            {
                "step_number": 8,
                "title": "🧠 Step 8: Save to Memory",
                "description": "Store this conversation exchange for context in future queries",
                "active_component": "memory",
                "details": """
                    Conversation Memory saves this exchange:
                    
                    Session: session_1736920965
                    File: ./memory/session_1736920965.json
                    
                    Exchange stored:
                    {
                        "user": "What documents do I need...",
                        "agent": "For ICICI HFC salaried home loan...",
                        "agent_type": "knowledge",
                        "timestamp": "2026-01-15T12:22:45"
                    }
                    
                    Why? If Priya asks a follow-up like:
                    "What about income proof?"
                    
                    The system knows she's still talking about salaried home loans!
                """,
                "code_snippet": """
# Save to conversation memory
memory.add_exchange(
    session_id=session_id,
    user_query=query,
    agent_response=answer,
    agent_type='knowledge'
)
                """,
                "duration": 0.5
            },
            
            {
                "step_number": 9,
                "title": "✅ Step 9: Return Response to User",
                "description": "Display the final answer to Priya with source citations",
                "active_component": "user",
                "details": """
                    Final Response Package:
                    
                    ✅ Answer: Comprehensive list of required documents
                    ✅ Sources: 3 document chunks cited
                    ✅ Agent: Knowledge Agent
                    ✅ Response Time: 4.3 seconds
                    ✅ Confidence: High (94.3% max relevance)
                    
                    Priya now sees her answer on screen with source documents!
                    
                    Total Journey: 9 steps, 4.3 seconds, multiple systems coordinated
                """,
                "code_snippet": """
# Return to user
return {
    'answer': answer,
    'sources': sources,
    'agent': 'knowledge',
    'response_time': 4.3
}
                """,
                "duration": 1.0
            }
        ]
    },
    
    # =========================================================================
    # SCENARIO 2: Marketing Agent Workflow
    # =========================================================================
    
    "marketing_query": {
        "title": "🎨 Story 2: Bank Manager Requests Marketing Campaign",
        "description": """
            Rajesh is a bank marketing manager who needs an email campaign
            targeting young professionals. Watch how the Marketing Agent
            creates creative content without using the knowledge base.
        """,
        "persona": {
            "name": "Rajesh",
            "age": 35,
            "occupation": "Marketing Manager",
            "goal": "Create email campaign"
        },
        "query": "Create an email campaign for home loans targeting young professionals aged 25-35",
        "expected_agent": "marketing",
        "steps": [
            {
                "step_number": 1,
                "title": "📝 Step 1: User Query Received",
                "description": "Rajesh requests a marketing campaign",
                "active_component": "user",
                "details": "Query: 'Create an email campaign for home loans targeting young professionals aged 25-35'",
                "code_snippet": "query = user_input.get_text()",
                "duration": 0.5
            },
            {
                "step_number": 2,
                "title": "🤖 Step 2: Supervisor Classification",
                "description": "Supervisor identifies this as a marketing request",
                "active_component": "supervisor",
                "details": """
                    Query Analysis:
                    - Keywords detected: "create", "email campaign", "targeting"
                    - Intent: Content generation (not information retrieval)
                    
                    Classification: MARKETING query
                    Decision: Route to Marketing Agent ✓
                    
                    Note: Marketing queries don't need ChromaDB retrieval,
                    they use the LLM's creative generation capabilities.
                """,
                "code_snippet": """
classification = classify_query(query)
if 'marketing' in classification:
    return route_to_marketing_agent()
                """,
                "duration": 1.0
            },
            {
                "step_number": 3,
                "title": "🎨 Step 3: Marketing Agent - Parse Parameters",
                "description": "Extract campaign details from the query",
                "active_component": "marketing_agent",
                "details": """
                    Parameter Extraction:
                    
                    Campaign Type: email
                    (detected keywords: "email campaign")
                    
                    Target Audience: young_professionals
                    (detected: "young professionals aged 25-35")
                    
                    Product: home_loan
                    (detected: "home loans")
                    
                    These parameters guide the LLM's creative generation.
                """,
                "code_snippet": """
# Parse campaign parameters
campaign_type = extract_type(query)  # 'email'
audience = extract_audience(query)   # 'young_professionals'
                """,
                "duration": 1.0
            },
            {
                "step_number": 4,
                "title": "🧠 Step 4: Marketing Agent - LLM Generation",
                "description": "Generate creative marketing content using LLM",
                "active_component": "marketing_agent",
                "details": """
                    Creative Generation Process:
                    
                    1. Load campaign template for email + young_professionals
                    2. Create detailed prompt with:
                       - Target audience characteristics
                       - Product benefits
                       - Call-to-action requirements
                    3. Send to Groq LLM for generation
                    4. LLM creates complete email campaign
                    
                    Generated Content Includes:
                    ✓ Subject line
                    ✓ Email body with personalization
                    ✓ Key selling points
                    ✓ Call-to-action
                    ✓ Disclaimer
                    
                    Generation Time: 2.1 seconds
                """,
                "code_snippet": """
# Generate marketing content
template = get_template(campaign_type, audience)
prompt = create_marketing_prompt(template, product)
campaign = llm.generate(prompt)
                """,
                "duration": 2.5
            },
            {
                "step_number": 5,
                "title": "💾 Step 5: Cache & Log",
                "description": "Save campaign to cache and log the operation",
                "active_component": "cache",
                "details": """
                    Similar to knowledge queries:
                    ✓ Saved to cache (./cache/response_cache.json)
                    ✓ Logged to observability (./logs/)
                    
                    But note: Marketing content is usually unique per request,
                    so cache hits are less common than knowledge queries.
                    
                    Each campaign is tailored to specific parameters.
                """,
                "code_snippet": """
cache.set(query, 'marketing', campaign)
monitor.log_query(query, 'marketing', 2.1, True)
                """,
                "duration": 1.0
            },
            {
                "step_number": 6,
                "title": "✅ Step 6: Return Campaign to User",
                "description": "Display the generated campaign content",
                "active_component": "user",
                "details": """
                    Rajesh receives a complete email campaign:
                    
                    📧 Subject: "Your Dream Home Awaits - Special Rates for Young Professionals"
                    
                    📝 Email Body: Personalized content highlighting:
                       - Low interest rates
                       - Quick approval process
                       - Flexible EMI options
                       - Success stories from peers
                    
                    ✅ Call-to-Action: "Apply Now" button with link
                    
                    Total Time: 5.1 seconds
                    Ready to use immediately!
                """,
                "code_snippet": """
return {
    'answer': campaign_content,
    'agent': 'marketing',
    'response_type': 'campaign'
}
                """,
                "duration": 1.0
            }
        ]
    },
    
    # =========================================================================
    # SCENARIO 3: Cache Hit Demo
    # =========================================================================
    
    "cache_demo": {
        "title": "💾 Story 3: Lightning-Fast Cache Response",
        "description": """
            Amit asks the same question that Priya asked earlier.
            Watch how the cache provides an instant response without
            repeating the expensive LLM generation process.
        """,
        "persona": {
            "name": "Amit",
            "age": 32,
            "occupation": "Teacher",
            "goal": "Quick answer"
        },
        "query": "What documents do I need for a salaried home loan at ICICI?",
        "expected_agent": "cached",
        "steps": [
            {
                "step_number": 1,
                "title": "📝 Step 1: User Query (Same as Before)",
                "description": "Amit asks the exact same question Priya asked",
                "active_component": "user",
                "details": "Query: 'What documents do I need for a salaried home loan at ICICI?'\n\nThis is IDENTICAL to Priya's query from Story 1.",
                "code_snippet": "query = user_input.get_text()",
                "duration": 0.5
            },
            {
                "step_number": 2,
                "title": "🤖 Step 2: Supervisor Classification",
                "description": "Quick classification (knowledge query)",
                "active_component": "supervisor",
                "details": "Classification: KNOWLEDGE query\nRouting to: Knowledge Agent",
                "code_snippet": "agent_type = classify(query)  # 'knowledge'",
                "duration": 0.5
            },
            {
                "step_number": 3,
                "title": "💾 Step 3: Cache HIT! ⚡",
                "description": "Cache finds the exact answer from Priya's query!",
                "active_component": "cache",
                "details": """
                    🎯 CACHE HIT!
                    
                    Cache Lookup:
                    - Generated cache key: md5('what documents...' + 'knowledge')
                    - Found in cache: YES ✓
                    - Cached at: 12:22:45 (5 minutes ago)
                    - TTL remaining: 23 hours 55 minutes
                    
                    Cached Response Retrieved:
                    "For ICICI HFC salaried home loan, you need: PAN Card, Aadhaar..."
                    
                    ⚡ Response Time: 0.09 seconds (instant!)
                    
                    Comparison:
                    - First time (Priya): 4.3 seconds
                    - Cache hit (Amit): 0.09 seconds
                    - Speedup: 47.8x faster!
                    
                    Cost Saved:
                    - No ChromaDB query needed
                    - No LLM API call needed
                    - ~$0.002 saved per query
                """,
                "code_snippet": """
cache_key = hash_query(query, 'knowledge')
cached = cache.get(cache_key)
if cached:
    return cached  # 0.09s total!
                """,
                "duration": 2.0
            },
            {
                "step_number": 4,
                "title": "✅ Step 4: Instant Response",
                "description": "Return cached answer immediately",
                "active_component": "user",
                "details": """
                    Amit receives the SAME high-quality answer as Priya,
                    but 47x faster!
                    
                    Response Package:
                    ✅ Answer: Complete document list
                    ✅ Source: Cache (not re-generated)
                    ✅ Response Time: 0.09 seconds
                    ✅ Quality: Identical to original
                    
                    This is why caching is crucial for production systems:
                    - Better user experience (faster)
                    - Lower costs (fewer API calls)
                    - Same answer quality
                """,
                "code_snippet": """
return {
    'answer': cached_answer,
    'agent': 'cached',
    'from_cache': True,
    'response_time': 0.09
}
                """,
                "duration": 1.0
            }
        ]
    }
}

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_component_color(component_name: str, active_component: str) -> str:
    """
    Returns the CSS background color for a component box based on whether
    it's currently active in the story.
    
    Parameters:
    -----------
    component_name : str
        Name of the component ('user', 'supervisor', 'knowledge_agent', etc.)
    active_component : str
        Which component is currently active in this step
        
    Returns:
    --------
    str
        Hex color code (like '#90EE90' for green)
        
    Logic:
    ------
    If component is active: return green (it's "working" right now)
    If component is not active: return gray (it's idle)
    
    Why we need this:
    This creates the visual "highlighting" effect where the active component
    lights up green while others stay gray. Users can SEE the flow of data.
    """
    if component_name == active_component:
        # This component is active in the current step
        return '#90EE90'  # Light green color
    else:
        # This component is inactive (idle)
        return '#D3D3D3'  # Light gray color

def get_component_icon(component_name: str) -> str:
    """
    Returns an emoji icon for each system component.
    
    Parameters:
    -----------
    component_name : str
        Name of the component
        
    Returns:
    --------
    str
        Emoji character
        
    Why emojis?
    Makes the UI more friendly and visually distinctive.
    Each component has its own recognizable icon.
    """
    icons = {
        'user': '👤',
        'supervisor': '🤖',
        'knowledge_agent': '📚',
        'marketing_agent': '🎨',
        'cache': '💾',
        'memory': '🧠',
        'observability': '📊',
        'chromadb': '🗄️',
        'llm': '🧠'
    }
    # Dictionary mapping component names to emoji icons
    
    return icons.get(component_name, '📦')
    # .get(name, default) returns the icon for this component
    # If component not in dictionary, return generic box emoji '📦'

# ==============================================================================
# MAIN RENDERING FUNCTION
# ==============================================================================

def render_storyboard(supervisor_agent):
    """
    Main function that renders the entire Story Demo tab.
    
    This creates an interactive storyboard where users can:
    1. Select a scenario (Knowledge/Marketing/Cache demo)
    2. Play through the scenario step-by-step
    3. See visual component highlighting
    4. Read detailed explanations of each step
    5. View simulated code snippets
    
    Parameters:
    -----------
    supervisor_agent : SupervisorAgent
        The supervisor instance (needed to actually run queries if desired)
        
    Returns:
    --------
    None
        Just displays UI elements
    """
    
    # ==========================================================================
    # PAGE HEADER
    # ==========================================================================
    
    st.title("🎬 Story Demo - Multi-Agent System in Action")
    
    st.markdown("""
        Watch how different queries flow through the multi-agent system.
        Each story demonstrates a different use case with step-by-step visualization.
        
        **Learn How:**
        - The Supervisor routes queries to the right agent
        - Knowledge Agent uses RAG (Retrieval Augmented Generation)
        - Marketing Agent creates creative content
        - Cache speeds up repeated queries
        - Memory maintains conversation context
        - Observability tracks everything
    """)
    
    st.markdown("---")
    
    # ==========================================================================
    # SCENARIO SELECTION
    # ==========================================================================
    
    st.subheader("📖 Select a Story Scenario")
    
    # Create tabs for each scenario
    scenario_tabs = st.tabs([
        "📚 Knowledge Query",   # Tab 1
        "🎨 Marketing Query",   # Tab 2
        "💾 Cache Demo"         # Tab 3
    ])
    # st.tabs() creates horizontal tabs at the top
    # Returns a list of tab objects we can use with "with" statement
    
    # Map each tab to its scenario key
    scenario_keys = ["knowledge_query", "marketing_query", "cache_demo"]
    
    # Loop through tabs and render each scenario
    for tab_index, tab in enumerate(scenario_tabs):
        # enumerate gives us index (0, 1, 2) and the tab object
        
        with tab:
            # Everything indented here appears in this tab
            
            scenario_key = scenario_keys[tab_index]
            # Get the scenario key for this tab
            
            scenario = STORY_SCENARIOS[scenario_key]
            # Get the full scenario dictionary from our database above
            
            # Display scenario details
            st.markdown(f"### {scenario['title']}")
            st.markdown(scenario['description'])
            
            # Show persona card
            st.markdown("#### 👤 Persona")
            persona = scenario['persona']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Name", persona['name'])
            with col2:
                st.metric("Age", persona['age'])
            with col3:
                st.metric("Occupation", persona['occupation'])
            with col4:
                st.metric("Goal", persona['goal'])
            
            # Show the query
            st.markdown("#### 💬 Query")
            st.info(f"**\"{scenario['query']}\"**")
            
            st.markdown("---")
            
            # =================================================================
            # PLAYBACK CONTROLS
            # =================================================================
            
            st.subheader("🎮 Story Playback Controls")
            
            # Initialize session state for this scenario if not exists
            state_key = f"story_{scenario_key}"
            # Create unique session state key for this scenario
            # Like "story_knowledge_query"
            
            if state_key not in st.session_state:
                # First time loading this scenario
                st.session_state[state_key] = {
                    'current_step': 0,      # Which step we're on (0-based index)
                    'is_playing': False,    # Is auto-play active?
                    'completed': False      # Have we finished all steps?
                }
            
            # Get state for this scenario
            state = st.session_state[state_key]
            # Shorthand variable for easier access
            
            # Control buttons
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("▶️ Play", key=f"play_{scenario_key}"):
                    # Start auto-playing through steps
                    state['is_playing'] = True
                    state['current_step'] = 0  # Start from beginning
                    state['completed'] = False
                    st.rerun()  # Refresh to start playing
            
            with col2:
                if st.button("⏸️ Pause", key=f"pause_{scenario_key}"):
                    # Stop auto-play
                    state['is_playing'] = False
                    st.rerun()
            
            with col3:
                if st.button("⏭️ Next Step", key=f"next_{scenario_key}"):
                    # Manual step forward
                    if state['current_step'] < len(scenario['steps']) - 1:
                        # If not on last step
                        state['current_step'] += 1
                        # Move to next step (increment by 1)
                    else:
                        # Already on last step
                        state['completed'] = True
                    state['is_playing'] = False  # Stop auto-play
                    st.rerun()
            
            with col4:
                if st.button("⏮️ Previous", key=f"prev_{scenario_key}"):
                    # Manual step backward
                    if state['current_step'] > 0:
                        # If not on first step
                        state['current_step'] -= 1
                        # Move back one step
                    state['is_playing'] = False
                    st.rerun()
            
            with col5:
                if st.button("🔄 Reset", key=f"reset_{scenario_key}"):
                    # Reset to beginning
                    state['current_step'] = 0
                    state['is_playing'] = False
                    state['completed'] = False
                    st.rerun()
            
            # Progress bar
            progress = (state['current_step'] + 1) / len(scenario['steps'])
            # Calculate percentage complete
            # +1 because steps are 0-indexed
            # Divide by total steps to get 0.0 to 1.0
            
            st.progress(progress)
            # st.progress() shows a visual progress bar
            # Takes value from 0.0 (empty) to 1.0 (full)
            
            st.caption(f"Step {state['current_step'] + 1} of {len(scenario['steps'])}")
            # Show "Step 3 of 9" for example
            
            st.markdown("---")
            
            # =================================================================
            # VISUAL COMPONENT DIAGRAM
            # =================================================================
            
            st.subheader("🔄 System Component Flow")
            
            # Get current step
            current_step = scenario['steps'][state['current_step']]
            # Get the step dictionary for the current step
            
            active_comp = current_step['active_component']
            # Which component is active in this step?
            
            # Create visual diagram with colored boxes
            # We'll show all components in a flow diagram
            
            st.markdown("#### Data Flow Visualization")
            
            # Row 1: User Input
            col = st.columns(1)[0]
            with col:
                color = get_component_color('user', active_comp)
                icon = get_component_icon('user')
                st.markdown(f"""
                    <div style="background-color: {color}; padding: 15px; 
                                border-radius: 10px; text-align: center; 
                                border: 3px solid {'#228B22' if active_comp == 'user' else '#808080'};">
                        <h3>{icon} User Input</h3>
                    </div>
                """, unsafe_allow_html=True)
            
            # Arrow down
            st.markdown("<div style='text-align: center; font-size: 2em;'>⬇️</div>", 
                       unsafe_allow_html=True)
            
            # Row 2: Supervisor
            col = st.columns(1)[0]
            with col:
                color = get_component_color('supervisor', active_comp)
                icon = get_component_icon('supervisor')
                st.markdown(f"""
                    <div style="background-color: {color}; padding: 15px; 
                                border-radius: 10px; text-align: center;
                                border: 3px solid {'#228B22' if active_comp == 'supervisor' else '#808080'};">
                        <h3>{icon} Supervisor Agent</h3>
                        <p style='margin: 0;'>Query Classification & Routing</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Arrow down (splits)
            st.markdown("<div style='text-align: center; font-size: 2em;'>⬇️</div>", 
                       unsafe_allow_html=True)
            
            # Row 3: Agents (side by side)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                color = get_component_color('knowledge_agent', active_comp)
                icon = get_component_icon('knowledge_agent')
                st.markdown(f"""
                    <div style="background-color: {color}; padding: 15px; 
                                border-radius: 10px; text-align: center;
                                border: 3px solid {'#228B22' if active_comp == 'knowledge_agent' else '#808080'};">
                        <h4>{icon} Knowledge Agent</h4>
                        <p style='margin: 0; font-size: 0.9em;'>RAG Pipeline</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                color = get_component_color('marketing_agent', active_comp)
                icon = get_component_icon('marketing_agent')
                st.markdown(f"""
                    <div style="background-color: {color}; padding: 15px; 
                                border-radius: 10px; text-align: center;
                                border: 3px solid {'#228B22' if active_comp == 'marketing_agent' else '#808080'};">
                        <h4>{icon} Marketing Agent</h4>
                        <p style='margin: 0; font-size: 0.9em;'>Content Generation</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                color = get_component_color('cache', active_comp)
                icon = get_component_icon('cache')
                st.markdown(f"""
                    <div style="background-color: {color}; padding: 15px; 
                                border-radius: 10px; text-align: center;
                                border: 3px solid {'#228B22' if active_comp == 'cache' else '#808080'};">
                        <h4>{icon} Cache</h4>
                        <p style='margin: 0; font-size: 0.9em;'>Response Storage</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Row 4: Supporting Systems
            st.markdown("<div style='text-align: center; font-size: 2em; margin-top: 20px;'>⬇️</div>", 
                       unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                color = get_component_color('memory', active_comp)
                icon = get_component_icon('memory')
                st.markdown(f"""
                    <div style="background-color: {color}; padding: 10px; 
                                border-radius: 10px; text-align: center;
                                border: 2px solid {'#228B22' if active_comp == 'memory' else '#808080'};">
                        <p style='margin: 0;'>{icon} <b>Memory</b></p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                color = get_component_color('observability', active_comp)
                icon = get_component_icon('observability')
                st.markdown(f"""
                    <div style="background-color: {color}; padding: 10px; 
                                border-radius: 10px; text-align: center;
                                border: 2px solid {'#228B22' if active_comp == 'observability' else '#808080'};">
                        <p style='margin: 0;'>{icon} <b>Observability</b></p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                color = get_component_color('chromadb', active_comp)
                icon = get_component_icon('chromadb')
                st.markdown(f"""
                    <div style="background-color: {color}; padding: 10px; 
                                border-radius: 10px; text-align: center;
                                border: 2px solid {'#228B22' if active_comp == 'chromadb' else '#808080'};">
                        <p style='margin: 0;'>{icon} <b>ChromaDB</b></p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # =================================================================
            # CURRENT STEP DETAILS
            # =================================================================
            
            st.markdown(f"### {current_step['title']}")
            
            # Description in an info box
            st.info(current_step['description'])
            
            # Detailed explanation in an expandable section
            with st.expander("📖 Detailed Explanation", expanded=True):
                st.markdown(current_step['details'])
            
            # Code snippet
            if 'code_snippet' in current_step:
                with st.expander("💻 Code Example", expanded=False):
                    st.code(current_step['code_snippet'], language='python')
                    # st.code displays code with syntax highlighting
            
            # =================================================================
            # AUTO-PLAY LOGIC
            # =================================================================
            
            if state['is_playing'] and not state['completed']:
                # If auto-play is on AND we haven't finished
                
                # Wait for the duration specified in the step
                time.sleep(current_step['duration'])
                # Pause execution for N seconds (creates animation effect)
                
                # Move to next step
                if state['current_step'] < len(scenario['steps']) - 1:
                    state['current_step'] += 1
                    st.rerun()  # Refresh to show next step
                else:
                    # Reached the end
                    state['completed'] = True
                    state['is_playing'] = False
                    st.success("✅ Story Complete!")
                    st.balloons()  # Celebration!
                    st.rerun()
            
            # Show completion message
            if state['completed']:
                st.success("🎉 Story Complete! You've seen the full journey.")
                st.markdown("""
                    **Key Takeaways:**
                    - Multi-agent systems coordinate multiple specialized components
                    - Caching dramatically improves performance
                    - Memory enables contextual conversations
                    - Observability provides insights into system behavior
                """)

# ==============================================================================
# END OF STORYBOARD COMPONENT
# ==============================================================================
