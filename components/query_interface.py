"""
==============================================================================
QUERY INTERFACE COMPONENT - WHERE USERS ASK QUESTIONS
==============================================================================

Purpose: This file contains the code for the "Query Interface" tab.
         It's where users can:
         - Type questions about home loans
         - See AI-generated answers
         - View source documents used to generate the answer
         - Give feedback on responses

Location: second/components/query_interface.py

Called by: streamlit_app.py when "Query Interface" tab is selected

How it works:
1. User types a question
2. Question goes to Supervisor Agent
3. Supervisor decides which agent to use (Knowledge or Marketing)
4. Agent processes and returns answer
5. Answer is displayed with sources
6. User can give feedback

==============================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import streamlit as st  # For creating web UI elements
import time  # For measuring response time
from typing import Dict, Any, Optional  # For type hints (helps with code clarity)
# Dict means "dictionary", Any means "any type", Optional means "can be None"

# ==============================================================================
# MAIN RENDERING FUNCTION
# ==============================================================================

def render_query_interface(supervisor_agent, session_id: str):
    """
    Main function that creates and displays the entire Query Interface tab.
    
    Parameters:
    -----------
    supervisor_agent : SupervisorAgent
        The supervisor agent instance that routes queries to appropriate agents.
        Think of it as the "manager" that decides who should handle each question.
        
    session_id : str
        Unique identifier for this user session (like "session_1736920800").
        Used to track conversation history separately for each user.
        
    Returns:
    --------
    None
        This function doesn't return anything, it just displays UI elements.
        
    How it's called:
    ----------------
    From streamlit_app.py:
    render_query_interface(st.session_state.supervisor, st.session_state.current_session_id)
    """
    
    # ==========================================================================
    # SECTION 1: PAGE TITLE AND DESCRIPTION
    # ==========================================================================
    
    st.title("💬 Query Interface")
    # st.title() creates a large heading at the top
    
    st.markdown("""
        Ask questions about ICICI Home Finance products, eligibility, documents, or 
        request marketing campaigns. The AI will automatically route your query to 
        the appropriate specialized agent.
    """)
    # st.markdown() displays formatted text (supports bold, italic, etc.)
    # Triple quotes """ allow multi-line strings in Python
    
    st.markdown("---")  # Horizontal divider line
    
    # ==========================================================================
    # SECTION 2: SETTINGS SIDEBAR
    # ==========================================================================
    
    with st.sidebar:
        # Everything indented here appears in the left sidebar
        
        st.subheader("🔧 Query Settings")
        # Medium-sized heading for this section
        
        # Number of source documents to retrieve
        n_results = st.slider(
            # st.slider creates a draggable slider widget
            
            "Number of source documents:",
            # Label text shown above the slider
            
            min_value=1,    # Minimum value user can select
            max_value=10,   # Maximum value user can select
            value=3,        # Default value when page loads
            step=1,         # How much value changes per click (1, 2, 3...)
            
            help="How many relevant document chunks to retrieve from the database"
            # Tooltip text shown when user hovers over the (?) icon
        )
        
        # Filter by document type
        doc_type_filter = st.selectbox(
            # st.selectbox creates a dropdown menu
            
            "Filter by document type:",
            # Label text
            
            ["All", "salaried", "self_employed", "prime", "knowledge_hub"],
            # List of options for the dropdown
            # "All" means no filtering
            
            help="Filter documents by borrower type or category"
            # Tooltip explanation
        )
        
        # Filter by loan type
        loan_type_filter = st.selectbox(
            "Filter by loan type:",
            ["All", "new_loan", "top_up", "balance_transfer", "plot_loan", 
             "insta_top_up", "application", "eligibility"],
            help="Filter documents by specific loan product type"
        )
        
        # Show/hide advanced options
        show_sources = st.checkbox(
            # st.checkbox creates a checkable box (True when checked, False when not)
            
            "Show source documents",
            # Label text
            
            value=True,
            # Default state (True = checked by default)
            
            help="Display the document chunks used to generate the answer"
        )
        
        show_metadata = st.checkbox(
            "Show detailed metadata",
            value=False,  # Unchecked by default
            help="Show technical details like chunk IDs, distances, etc."
        )
    
    # ==========================================================================
    # SECTION 3: SAMPLE QUERIES SECTION
    # ==========================================================================
    
    st.subheader("💡 Try These Sample Queries")
    # Subheading for example questions
    
    # Define sample questions users can click
    sample_queries = [
        "What documents are needed for a salaried home loan?",
        "Eligibility criteria for self-employed applicants",
        "How to apply for home loan online?",
        "Create an email campaign for young professionals",
        "What are the benefits of balance transfer?",
        "Generate a social media post about top-up loans"
    ]
    # This is a Python list containing 6 string items (sample questions)
    
    # Create 3 columns to display samples in a grid layout
    col1, col2, col3 = st.columns(3)
    # st.columns(3) creates 3 equal-width columns
    # We assign them to col1, col2, col3 variables to use separately
    
    # Loop through sample queries and create buttons
    for idx, sample in enumerate(sample_queries):
        # enumerate() gives us both the index (0, 1, 2...) and the item
        # idx will be 0, 1, 2, 3, 4, 5
        # sample will be each question string
        
        # Determine which column to use based on index
        if idx % 3 == 0:
            # % is modulo operator (remainder after division)
            # idx % 3 gives: 0, 1, 2, 0, 1, 2 for idx 0-5
            # So idx 0, 3 go to column 1
            column = col1
        elif idx % 3 == 1:
            # idx 1, 4 go to column 2
            column = col2
        else:
            # idx 2, 5 go to column 3
            column = col3
        
        with column:
            # Place the button in the selected column
            
            if st.button(sample, key=f"sample_{idx}", use_container_width=True):
                # st.button creates a clickable button
                # sample = the text shown on the button
                # key = unique identifier (required when you have multiple buttons)
                # use_container_width=True makes button stretch to full column width
                # The if checks if this button was clicked
                
                st.session_state.query_input = sample
                # Save the clicked question to session state
                # This will populate the text input below
                
                st.rerun()
                # Rerun the entire script to show the updated query_input
                # This is how Streamlit updates the UI
    
    st.markdown("---")  # Divider line
    
    # ==========================================================================
    # SECTION 4: QUERY INPUT
    # ==========================================================================
    
    st.subheader("🔍 Your Query")
    
    # Text input box for user to type their question
    query = st.text_input(
        # st.text_input creates a single-line text input box
        
        "Ask your question:",
        # Label text
        
        # value=st.session_state.get('query_input', ''),
        value=st.session_state.selected_query,  # ✅ Use persistent state
        # Default value in the text box
        # st.session_state.get('query_input', '') means:
        # - Try to get 'query_input' from session state
        # - If it doesn't exist, use empty string ''
        # This is how we populate it when sample button is clicked
        
        placeholder="Example: What documents do I need for a salaried home loan?",
        # Gray placeholder text shown when box is empty
        
        key="main_query_input",
        # Unique key for this widget
        
        help="Type any question about ICICI home loans or request a marketing campaign"
    )
    
    # Clear the temporary query_input from session state after reading it
    if 'query_input' in st.session_state:
        # If the key exists (it was set by a sample button click)
        del st.session_state.query_input
        # Delete it so it doesn't interfere with next query
    
    # ==========================================================================
    # SECTION 5: SUBMIT BUTTON AND QUERY PROCESSING
    # ==========================================================================
    
    # Create two columns: one for submit button, one for clear history button
    col_submit, col_clear = st.columns([3, 1])
    # [3, 1] means first column is 3x wider than second column
    
    with col_submit:
        submit_button = st.button(
            "🚀 Submit Query", 
            type="primary",  # Makes button blue/prominent
            use_container_width=True
        )
    
    with col_clear:
        if st.button("🗑️ Clear History", use_container_width=True):
            # Button to reset query history
            st.session_state.query_history = []
            # Reset to empty list
            st.success("History cleared!")
            st.rerun()
    
    # ==========================================================================
    # SECTION 6: PROCESS QUERY WHEN SUBMIT IS CLICKED
    # ==========================================================================
    
    if submit_button and query:
        # Only process if:
        # 1. Submit button was clicked (submit_button is True)
        # 2. AND query is not empty (query has text)
        # The "and" means BOTH conditions must be true
        
        # Build metadata filters dictionary
        filters = {}
        # Start with empty dictionary {}
        
        if doc_type_filter != "All":
            # If user selected a specific document type (not "All")
            filters['doc_type'] = doc_type_filter
            # Add it to filters dictionary
            # Result: {'doc_type': 'salaried'} for example
        
        if loan_type_filter != "All":
            # If user selected a specific loan type
            filters['loan_type'] = loan_type_filter
            # Add to filters
            # Result: {'doc_type': 'salaried', 'loan_type': 'new_loan'}
        
        # If filters is still empty {}, set to None
        if not filters:
            # not filters checks if dictionary is empty
            # Empty dict {} is considered "falsy" in Python
            filters = None
        
        # Show a spinner while processing (visual feedback to user)
        with st.spinner("🤔 Processing your query... Routing to appropriate agent..."):
            # Everything indented here runs while showing the spinner animation
            
            try:
                # try block: attempt to run code, catch errors if they occur
                
                # Start timing the request
                start_time = time.time()
                # time.time() returns current time in seconds (like 1736920800.123)
                
                # Send query to supervisor agent
                result = supervisor_agent.route_query(
                    # Call the route_query method of supervisor_agent
                    # This is where the magic happens!
                    
                    query=query,           # The user's question
                    session_id=session_id, # Session identifier
                    n_results=n_results,   # How many docs to retrieve
                    filters=filters        # Metadata filters (or None)
                )
                # result is a dictionary containing:
                # - 'agent': which agent handled it ('knowledge' or 'marketing')
                # - 'answer': the generated response
                # - 'sources': list of source documents (for knowledge agent)
                # - other metadata
                
                # Calculate response time
                response_time = time.time() - start_time
                # Current time minus start time = elapsed seconds
                
                # Add to query history
                st.session_state.query_history.append({
                    # .append() adds an item to the end of a list
                    
                    'query': query,                    # What user asked
                    'agent': result.get('agent'),      # Which agent responded
                    'response_time': response_time,    # How long it took
                    'timestamp': time.time()           # When it happened
                })
                # Now query_history list has one more dictionary in it
                
                # ==========================================================
                # DISPLAY RESULTS
                # ==========================================================
                
                st.markdown("---")
                
                # Show which agent handled the query
                agent_type = result.get('agent', 'unknown')
                # .get('agent', 'unknown') means:
                # - Try to get value for key 'agent'
                # - If key doesn't exist, use 'unknown' as default
                
                # Display agent info with emoji
                if agent_type == 'knowledge':
                    st.info(f"📚 **Routed to:** Knowledge Agent | ⏱️ **Response Time:** {response_time:.2f}s")
                    # :.2f formats the number to 2 decimal places (like 1.23)
                    
                elif agent_type == 'marketing':
                    st.info(f"🎨 **Routed to:** Marketing Agent | ⏱️ **Response Time:** {response_time:.2f}s")
                    
                elif agent_type == 'cached':
                    st.success(f"💾 **Cache Hit!** | ⏱️ **Response Time:** {response_time:.2f}s (instant)")
                    # Cached responses are very fast
                
                # Display the answer in a nice box
                st.markdown("### ✨ Answer:")
                # st.markdown(f"""
                #     <div style="background-color: #f0f2f6; padding: 1.5rem; 
                #                 border-radius: 10px; border-left: 4px solid #1f77b4;">
                #         {result['answer']}
                #     </div>
                # """, unsafe_allow_html=True)
                # st.markdown(
                #     f'<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                #     f'padding: 2px; border-radius: 10px;">'
                #     f'<div style="background-color: white; padding: 20px; border-radius: 8px;">'
                #     f'{result["answer"]}'
                #     f'</div></div>',
                #     unsafe_allow_html=True)
                st.success(result['answer'])  # Green box, auto-height
                                            
                                            
                # This creates a styled box with the answer
                # result['answer'] contains the AI-generated response
                
                # ==========================================================
                # DISPLAY SOURCE DOCUMENTS (if available and enabled)
                # ==========================================================
                
                if show_sources and 'sources' in result and result['sources']:
                    # Three conditions (all must be true):
                    # 1. show_sources checkbox is checked
                    # 2. 'sources' key exists in result dictionary
                    # 3. sources list is not empty
                    
                    st.markdown("---")
                    st.markdown("### 📄 Source Documents")
                    st.caption(f"Retrieved {len(result['sources'])} relevant document chunks")
                    # st.caption shows small gray text
                    # len(result['sources']) counts items in sources list
                    
                    # Loop through each source document
                    for idx, source in enumerate(result['sources'], start=1):
                        # enumerate with start=1 gives: 1, 2, 3... instead of 0, 1, 2...
                        # idx will be 1, 2, 3...
                        # source is each dictionary in the sources list
                        
                        # Create expandable section for each source
                        with st.expander(
                            # st.expander creates a collapsible section
                            
                            f"📄 Source {idx}: {source['source']} "
                            f"(Relevance: {source['relevance']:.1f}%)",
                            # Title shown on the expander
                            # source['source'] = filename
                            # source['relevance'] = similarity score as percentage
                            
                            expanded=(idx == 1)
                            # First source (idx==1) starts expanded, others collapsed
                        ):
                            # Everything indented here appears inside the expander
                            
                            # Show metadata in 3 columns
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Document Type", source.get('doc_type', 'N/A'))
                                # st.metric shows a value in a nice box
                                # source.get('doc_type', 'N/A') gets doc_type or 'N/A' if missing
                            
                            with col2:
                                st.metric("Loan Type", source.get('loan_type', 'N/A'))
                            
                            with col3:
                                st.metric("Relevance", f"{source['relevance']:.1f}%")
                            
                            # Show document preview
                            st.markdown("**Document Preview:**")
                            st.text_area(
                                # st.text_area creates a multi-line text box
                                
                                "Preview",
                                # Label (we hide it below)
                                
                                value=source.get('preview', source.get('content', 'No preview available')[:500]),
                                # Show preview if available, else first 500 chars of content
                                # [:500] takes first 500 characters
                                
                                height=150,
                                # Height of text box in pixels
                                
                                key=f"source_{idx}",
                                # Unique key for each text area
                                
                                label_visibility="collapsed"
                                # Hide the "Preview" label
                            )
                            
                            # Show detailed metadata if enabled
                            if show_metadata:
                                st.json(source)
                                # st.json displays dictionary in formatted JSON view
                                # Useful for debugging/seeing all data
                
                # ==========================================================
                # FEEDBACK SECTION
                # ==========================================================
                
                st.markdown("---")
                st.markdown("### 👍 Rate This Response")
                
                # Create columns for feedback buttons
                col1, col2, col3, col4, col5 = st.columns(5)
                # 5 columns for 5 rating options
                
                # Rating buttons
                ratings = [
                    ("⭐", 1, col1),
                    ("⭐⭐", 2, col2),
                    ("⭐⭐⭐", 3, col3),
                    ("⭐⭐⭐⭐", 4, col4),
                    ("⭐⭐⭐⭐⭐", 5, col5)
                ]
                # List of tuples (3 items each)
                # Each tuple: (display_text, rating_value, column_object)
                
                for emoji, rating, col in ratings:
                    # Unpack each tuple into 3 variables
                    
                    with col:
                        if st.button(emoji, key=f"rating_{rating}", use_container_width=True):
                            # Button for each star rating
                            
                            # Submit feedback to supervisor
                            supervisor_agent.submit_feedback(
                                session_id=session_id,
                                query=query,
                                response=result['answer'],
                                rating=rating,
                                agent_type=agent_type
                            )
                            # This saves the rating to feedback_system.py
                            
                            st.success(f"Thank you! Rated {rating}/5 ⭐")
                            st.balloons()
                            # st.balloons() shows celebratory falling balloons animation!
                
                # Optional comment box
                feedback_comment = st.text_area(
                    "Additional feedback (optional):",
                    placeholder="Share your thoughts about this response...",
                    height=100,
                    key="feedback_comment"
                )
                
                if st.button("Submit Feedback Comment") and feedback_comment:
                    # If button clicked AND comment is not empty
                    
                    # Submit with default rating of 3 if not rated yet
                    supervisor_agent.submit_feedback(
                        session_id=session_id,
                        query=query,
                        response=result['answer'],
                        rating=3,  # Default neutral rating
                        comment=feedback_comment,
                        agent_type=agent_type
                    )
                    
                    st.success("Feedback submitted! Thank you.")
            
            except Exception as e:
                # If ANY error occurs in the try block, code jumps here
                # e contains the error object
                
                st.error(f"❌ **Error processing query:** {str(e)}")
                # Display error message to user
                # str(e) converts error object to readable string
                
                st.info("💡 **Troubleshooting tips:**")
                st.markdown("""
                    - Ensure ChromaDB is initialized (run `setup_chroma.py`)
                    - Check if documents are indexed (run `index_icici_docs.py`)
                    - Verify API keys in `config.py`
                    - Try a simpler query
                """)
    
    elif submit_button and not query:
        # If button clicked but query is empty
        # not query checks if query is empty string ''
        
        st.warning("⚠️ Please enter a query before submitting.")
        # st.warning shows yellow warning box
    
    # ==========================================================================
    # SECTION 7: QUERY HISTORY DISPLAY
    # ==========================================================================
    
    if st.session_state.query_history:
        # If query_history list is not empty (has items)
        
        st.markdown("---")
        st.subheader("📜 Query History (This Session)")
        
        # Show last 5 queries (most recent first)
        recent_queries = st.session_state.query_history[-5:]
        # [-5:] takes last 5 items from list
        # If list has less than 5, takes all
        
        recent_queries.reverse()
        # .reverse() flips the list order (newest first)
        
        for idx, hist_item in enumerate(recent_queries, start=1):
            # Loop through history items
            
            with st.expander(f"Query {idx}: {hist_item['query'][:60]}...", expanded=False):
                # Show first 60 characters in title
                # expanded=False means all start collapsed
                
                st.write(f"**Query:** {hist_item['query']}")
                st.write(f"**Agent:** {hist_item['agent']}")
                st.write(f"**Response Time:** {hist_item['response_time']:.2f}s")
                
                # Show timestamp in readable format
                from datetime import datetime
                timestamp = datetime.fromtimestamp(hist_item['timestamp'])
                # Convert Unix timestamp to datetime object
                st.write(f"**Time:** {timestamp.strftime('%I:%M:%S %p')}")
                # strftime formats time as "02:30:15 PM"

# ==============================================================================
# END OF QUERY INTERFACE COMPONENT
# ==============================================================================