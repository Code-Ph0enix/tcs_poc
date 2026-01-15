# """
# Query Demo Interface with RAG Agent
# Location: second/query_demo.py
# """

# import streamlit as st
# from vectorstore.retriever import FinancialRetriever
# from agents.knowledge_agent import KnowledgeAgent
# from config import *

# st.set_page_config(
#     page_title="ICICI HFC Home Loan Assistant",
#     page_icon="🏠",
#     layout="wide"
# )


# @st.cache_resource
# def init_retriever():
#     """Initialize retriever for direct search"""
#     return FinancialRetriever()


# @st.cache_resource
# def init_rag_agent():
#     """Initialize RAG agent for AI-powered answers"""
#     return KnowledgeAgent()


# # Initialize components
# retriever = init_retriever()


# st.title("🏠 ICICI HFC Home Loan Assistant")
# st.markdown("**Powered by ChromaDB + LLM RAG Pipeline**")
# st.markdown("---")


# # Sidebar
# with st.sidebar:
#     st.header("⚙️ Search Settings")
    
#     # Toggle between RAG and direct retrieval
#     use_rag = st.toggle(" AI Answer Generation (RAG)", value=True, help="Use LLM to generate natural answers from retrieved documents")
    
#     st.markdown("---")
    
#     n_results = st.slider("Number of results:", 1, 10, 3)
    
#     doc_type_filter = st.selectbox(
#         "Filter by type:",
#         ["All", "salaried", "self_employed", "prime", "knowledge_hub"]
#     )
    
#     loan_type_filter = st.selectbox(
#         "Filter by loan type:",
#         ["All", "new_loan", "top_up", "balance_transfer", "plot_loan", 
#          "insta_top_up", "application", "eligibility"]
#     )
    
#     st.markdown("---")
#     st.header(" Database Stats")
#     try:
#         collection = retriever.collection
#         st.metric("Total Chunks", collection.count())
#         st.metric("Bank", "ICICI HFC")
#         st.metric("Mode", " AI Assistant" if use_rag else "🔍 Direct Search")
#     except:
#         st.info("Database not initialized")


# # Main query interface
# query = st.text_input(
#     "🔍 Ask your question:",
#     placeholder="What documents are needed for ICICI salaried home loan?",
#     key="query_input"
# )


# if st.button("Search", type="primary", use_container_width=True):
#     if query:
#         # Build filters
#         filters = {}
#         if doc_type_filter != "All":
#             filters['doc_type'] = doc_type_filter
#         if loan_type_filter != "All":
#             filters['loan_type'] = loan_type_filter
        
#         # RAG MODE - AI-Generated Answer
#         if use_rag:
#             with st.spinner(" Generating AI answer..."):
#                 try:
#                     rag_agent = init_rag_agent()
#                     result = rag_agent.query(
#                         question=query,
#                         n_results=n_results,
#                         filters=filters if filters else None,
#                         return_sources=True
#                     )
                    
#                     # Display AI Answer
#                     st.success("✅ AI-Generated Answer")
                    
#                     st.markdown("###  Answer:")
#                     st.markdown(result['answer'])
                    
#                     # Display sources
#                     st.markdown("---")
#                     st.markdown("###  Source Documents")
                    
#                     for idx, source in enumerate(result['sources'], 1):
#                         with st.expander(
#                             f"📄 Source {idx}: {source['source']} (Relevance: {source['relevance']}%)",
#                             expanded=(idx == 1)
#                         ):
#                             col1, col2, col3 = st.columns(3)
#                             with col1:
#                                 st.metric("Doc Type", source['doc_type'])
#                             with col2:
#                                 st.metric("Loan Type", source['loan_type'])
#                             with col3:
#                                 st.metric("Relevance", f"{source['relevance']}%")
                            
#                             st.markdown("---")
#                             st.markdown("**Preview:**")
#                             st.text_area("Preview", source['preview'], height=150, key=f"source_{idx}", label_visibility="collapsed")
                    
#                 except Exception as e:
#                     st.error(f"❌ RAG Error: {str(e)}")
#                     st.info("💡 Try disabling AI mode in the sidebar for direct search")
        
#         # DIRECT RETRIEVAL MODE - Raw Results
#         else:
#             with st.spinner("🔍 Searching database..."):
#                 try:
#                     results = retriever.retrieve(
#                         query=query,
#                         n_results=n_results,
#                         filters=filters if filters else None
#                     )
                    
#                     st.success(f"✅ Found {len(results['documents'][0])} relevant results")
                    
#                     for idx, (doc, metadata, distance) in enumerate(zip(
#                         results['documents'][0],
#                         results['metadatas'][0],
#                         results['distances'][0]
#                     ), 1):
                        
#                         relevance_score = (1 - distance) * 100
                        
#                         with st.expander(
#                             f"📄 Result {idx}: {metadata.get('source', 'Unknown')} "
#                             f"(Relevance: {relevance_score:.1f}%)",
#                             expanded=(idx == 1)
#                         ):
#                             col1, col2, col3 = st.columns(3)
#                             with col1:
#                                 st.metric("Doc Type", metadata.get('doc_type', 'N/A'))
#                             with col2:
#                                 st.metric("Loan Type", metadata.get('loan_type', 'N/A'))
#                             with col3:
#                                 chunk_info = f"{metadata.get('chunk_index', 0) + 1}/{metadata.get('total_chunks', 1)}"
#                                 st.metric("Chunk", chunk_info)
                            
#                             st.markdown("---")
#                             st.markdown("**Retrieved Content:**")
#                             st.text_area("Content", doc, height=250, key=f"content_{idx}", label_visibility="collapsed")
                    
#                 except Exception as e:
#                     st.error(f"❌ Search Error: {str(e)}")
#     else:
#         st.warning("⚠️ Please enter a query")


# # Sample queries
# st.markdown("---")
# st.subheader("💡 Sample Queries")

# col1, col2 = st.columns(2)

# sample_queries = [
#     "What documents are needed for ICICI salaried home loan?",
#     "Self-employed home loan eligibility criteria",
#     "How to apply for home loan online?",
#     "Balance transfer benefits ICICI HFC",
#     "Plot loan requirements for self-employed",
#     "Top-up loan process for salaried",
#     "ICICI Prime home loan features",
#     "Insta top-up loan eligibility"
# ]

# # ✅ FIXED: Helper function to handle state update via callback
# def set_query(question):
#     st.session_state.query_input = question

# for i, sq in enumerate(sample_queries):
#     col = col1 if i % 2 == 0 else col2
#     with col:
#         # ✅ FIXED: using on_click callback instead of modifying state in the loop body
#         st.button(
#             sq, 
#             key=f"sample_{i}", 
#             use_container_width=True,
#             on_click=set_query,
#             args=(sq,)
#         )


# # Footer
# st.markdown("---")
# st.markdown(
#     """
#     <div style='text-align: center; color: #666;'>
#     <small>💡 Toggle AI mode in sidebar to switch between RAG answers and direct search results</small>
#     </div>
#     """,
#     unsafe_allow_html=True
# )











"""
Multi-Agent Demo Interface
Location: second/demo_multi_agent.py
Shows both Knowledge Agent (RAG) and Marketing Agent
"""

import streamlit as st
from agents.supervisor_agent import SupervisorAgent
import time

st.set_page_config(
    page_title="Multi-Agent Banking Assistant",
    page_icon="🤖",
    layout="wide"
)

# ✅ FIXED: Helper function to handle state update via callback
def set_query(question):
    st.session_state.query_input = question

@st.cache_resource
def init_supervisor():
    """Initialize supervisor with all agents"""
    return SupervisorAgent(
        enable_memory=True,
        enable_cache=True,
        enable_monitoring=True,
        enable_feedback=True
    )


# Initialize supervisor
supervisor = init_supervisor()


# Custom CSS for agent differentiation
st.markdown("""
<style>
.knowledge-agent {
    background-color: #e3f2fd;
    border-left: 5px solid #2196F3;
    padding: 15px;
    border-radius: 5px;
}

.marketing-agent {
    background-color: #f3e5f5;
    border-left: 5px solid #9C27B0;
    padding: 15px;
    border-radius: 5px;
}

.cached-response {
    background-color: #fff9c4;
    border-left: 5px solid #FFC107;
    padding: 15px;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)


# Header
st.title("🤖 Multi-Agent Banking Assistant")
st.markdown("**Powered by Supervisor Orchestration + Specialized Agents**")
st.markdown("---")


# Sidebar - Agent Info
with st.sidebar:
    st.header("🎯 Agent System")
    
    st.markdown("""
    ### 🧠 Knowledge Agent
    - Answers banking questions
    - Uses RAG pipeline
    - Retrieves from 14 ICICI docs
    - 57 knowledge chunks
    
    ### 🎨 Marketing Agent
    - Generates campaigns
    - Creates promotional content
    - Email, Social Media, SMS, Blog
    
    ### 👨‍💼 Supervisor
    - Routes queries automatically
    - Classifies intent
    - Manages memory & cache
    """)
    
    st.markdown("---")
    
    # System stats
    st.header("📈 System Stats")
    
    # Memory stats
    if supervisor.enable_memory:
        session_id = st.session_state.get('session_id', 'demo_user')
        history = supervisor.memory.get_history(session_id)
        st.metric("💾 Memory", f"{len(history)} exchanges")
    
    # Cache stats
    if supervisor.enable_cache:
        cache_stats = supervisor.cache.get_stats()
        st.metric("🗂️ Cache", f"{cache_stats['total_entries']} entries")
    
    # Performance stats
    if supervisor.enable_monitoring:
        perf_stats = supervisor.monitor.get_stats()
        st.metric("⚡ Queries", perf_stats['total_queries'])
        st.metric("✅ Success Rate", f"{perf_stats['success_rate']}%")
    
    # Feedback stats
    if supervisor.enable_feedback:
        fb_stats = supervisor.feedback.get_feedback_stats()
        if fb_stats['total_feedbacks'] > 0:
            st.metric("👍 Satisfaction", f"{fb_stats['satisfaction_rate']}%")


# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"demo_user_{int(time.time())}"

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []


# Main interface
tab1, tab2, tab3 = st.tabs(["🔍 Query Interface", "💬 Conversation History", "📊 Analytics"])


with tab1:
    st.subheader("Ask a Question or Request a Campaign")
    
    # Query input
    query = st.text_area(
        "Your Query:",
        placeholder="Examples:\n- What documents are needed for home loan?\n- Create an email campaign for young professionals\n- What is the eligibility criteria?",
        height=100,
        key="query_input"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        submit_button = st.button("🚀 Submit Query", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear History", use_container_width=True)
    
    if clear_button:
        st.session_state.conversation_history = []
        supervisor.memory.clear_session(st.session_state.session_id)
        st.rerun()
    
    if submit_button and query:
        with st.spinner("🤖 Processing query..."):
            try:
                start_time = time.time()
                
                # Route query through supervisor
                result = supervisor.route_query(
                    query=query,
                    session_id=st.session_state.session_id,
                    n_results=3
                )
                
                response_time = time.time() - start_time
                
                # Store in conversation history
                st.session_state.conversation_history.append({
                    'query': query,
                    'result': result,
                    'response_time': response_time
                })
                
                # Display result
                agent_type = result['agent']
                
                # Header based on agent type
                if agent_type == 'cached':
                    st.markdown('<div class="cached-response">', unsafe_allow_html=True)
                    st.success("⚡ CACHED RESPONSE (Instant!)")
                elif agent_type == 'knowledge':
                    st.markdown('<div class="knowledge-agent">', unsafe_allow_html=True)
                    st.success("🧠 KNOWLEDGE AGENT (RAG Pipeline)")
                elif agent_type == 'marketing':
                    st.markdown('<div class="marketing-agent">', unsafe_allow_html=True)
                    st.success("🎨 MARKETING AGENT (Campaign Generator)")
                
                # Display response
                st.markdown(f"**Response Time:** {response_time:.2f}s")
                st.markdown("---")
                st.markdown("### Response:")
                st.markdown(result['answer'])
                
                # Show sources for knowledge agent
                if agent_type == 'knowledge' and 'sources' in result:
                    st.markdown("---")
                    st.markdown("### 📚 Sources:")
                    for idx, source in enumerate(result['sources'][:3], 1):
                        with st.expander(f"Source {idx}: {source.get('source', 'Unknown')}"):
                            st.text(source.get('preview', 'No preview available'))
                
                # Show campaign details for marketing agent
                if agent_type == 'marketing' and 'campaign' in result:
                    campaign = result['campaign']
                    st.markdown("---")
                    st.info(f"**Campaign Type:** {campaign['campaign_type']} | **Audience:** {campaign['target_audience']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Feedback section
                st.markdown("---")
                st.subheader("💭 Was this response helpful?")
                
                col1, col2, col3 = st.columns([1, 1, 3])
                
                with col1:
                    if st.button("👍 Yes", key=f"thumbs_up_{len(st.session_state.conversation_history)}"):
                        supervisor.submit_feedback(
                            session_id=st.session_state.session_id,
                            query=query,
                            response=result['answer'],
                            rating=5,
                            comment="Helpful!",
                            agent_type=agent_type
                        )
                        st.success("Thanks for your feedback! 👍")
                
                with col2:
                    if st.button("👎 No", key=f"thumbs_down_{len(st.session_state.conversation_history)}"):
                        supervisor.submit_feedback(
                            session_id=st.session_state.session_id,
                            query=query,
                            response=result['answer'],
                            rating=2,
                            comment="Not helpful",
                            agent_type=agent_type
                        )
                        st.warning("Thanks for your feedback! We'll improve.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Sample queries section
    st.markdown("---")
    st.subheader("💡 Try These Examples:")
    
    col1, col2 = st.columns(2)
    
    knowledge_queries = [
        "What documents are needed for self-employed home loan?",
        "Eligibility criteria for ICICI home loan?",
        "How to apply for plot loan?",
        "Balance transfer benefits?"
    ]
    
    marketing_queries = [
        "Create an email campaign for home loans targeting young professionals",
        "Generate a social media post about top-up loans",
        "Write an SMS campaign for balance transfer",
        "Create a blog post about home loan eligibility"
    ]
    
    with col1:
        st.markdown("📚 **Knowledge Questions:**")
        for i, q in enumerate(knowledge_queries):
            # ✅ FIXED: Using callback for state update
            st.button(
                q, 
                key=f"know_{i}", 
                use_container_width=True,
                on_click=set_query,
                args=(q,)
            )
    
    with col2:
        st.markdown("🎨 **Marketing Requests:**")
        for i, q in enumerate(marketing_queries):
            # ✅ FIXED: Using callback for state update
            st.button(
                q, 
                key=f"mark_{i}", 
                use_container_width=True,
                on_click=set_query,
                args=(q,)
            )


with tab2:
    st.subheader("💬 Conversation History")
    
    if st.session_state.conversation_history:
        for idx, item in enumerate(reversed(st.session_state.conversation_history), 1):
            agent_type = item['result']['agent']
            
            # Color-code by agent
            if agent_type == 'knowledge':
                icon = "🧠"
                color = "#2196F3"
            elif agent_type == 'marketing':
                icon = "🎨"
                color = "#9C27B0"
            else:
                icon = "⚡"
                color = "#FFC107"
            
            with st.expander(f"{icon} Query {len(st.session_state.conversation_history) - idx + 1}: {item['query'][:60]}..."):
                st.markdown(f"**Agent:** {agent_type.upper()}")
                st.markdown(f"**Response Time:** {item['response_time']:.2f}s")
                st.markdown("---")
                st.markdown(item['result']['answer'])
    else:
        st.info("No conversation history yet. Ask a question to get started!")


with tab3:
    st.subheader("📊 System Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    # Performance metrics
    if supervisor.enable_monitoring:
        perf_stats = supervisor.monitor.get_stats()
        
        with col1:
            st.metric("Total Queries", perf_stats['total_queries'])
            st.metric("Success Rate", f"{perf_stats['success_rate']}%")
        
        with col2:
            st.metric("Avg Response Time", f"{perf_stats['avg_response_time']}s")
            
            if 'by_agent' in perf_stats:
                for agent, data in perf_stats['by_agent'].items():
                    st.metric(f"{agent.title()} Queries", data['count'])
        
        with col3:
            # Cache stats
            if supervisor.enable_cache:
                cache_stats = supervisor.cache.get_stats()
                st.metric("Cache Entries", cache_stats['total_entries'])
            
            # Feedback stats
            if supervisor.enable_feedback:
                fb_stats = supervisor.feedback.get_feedback_stats()
                if fb_stats['total_feedbacks'] > 0:
                    st.metric("User Feedbacks", fb_stats['total_feedbacks'])
                    st.metric("Avg Rating", f"{fb_stats['avg_rating']}/5")
    
    # Show agent breakdown
    st.markdown("---")
    st.subheader("📈 Agent Performance Breakdown")
    
    if supervisor.enable_monitoring:
        perf_stats = supervisor.monitor.get_stats()
        
        if 'by_agent' in perf_stats and perf_stats['by_agent']:
            for agent, data in perf_stats['by_agent'].items():
                st.markdown(f"**{agent.upper()}:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Queries Handled", data['count'])
                with col2:
                    st.metric("Avg Response Time", f"{data['avg_time']}s")


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<small>
🤖 Powered by Multi-Agent Architecture | 
🧠 Knowledge Agent (RAG) + 🎨 Marketing Agent | 
👨‍💼 Supervisor Orchestration
</small>
</div>
""", unsafe_allow_html=True)