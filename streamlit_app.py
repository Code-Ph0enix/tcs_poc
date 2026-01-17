"""
==============================================================================
STREAMLIT MAIN APPLICATION - MULTI-AGENT AI SYSTEM DEMO
==============================================================================

Purpose: This is the MAIN file that runs your entire Streamlit web application.
         It creates a web interface with 3 tabs:
         1. Query Interface - Ask questions to the AI
         2. Story Demo - Watch how agents work together (storyboarding)
         3. Analytics Dashboard - See system performance metrics

Location: tcs_poc/streamlit_app.py

How to run: streamlit run streamlit_app.py

Author: Eeshanya Joshi
Date: January 15, 2026
==============================================================================
"""

# ==============================================================================
# SECTION 1: IMPORT LIBRARIES
# ==============================================================================
# These are like "ingredients" we need before we can cook our application

import streamlit as st  # Main library for creating web apps in Python
import sys  # System library to modify Python's path (where it looks for files)
import os   # Operating system library to work with file paths and directories
from pathlib import Path  # Modern way to handle file paths (better than strings)
import time  # Library to work with time (delays, timestamps, etc.)
import json  # Library to work with JSON data format (like dictionaries but can save to files)

# ==============================================================================
# SECTION 2: ADD PROJECT DIRECTORIES TO PYTHON PATH
# ==============================================================================
# Why? Because our project files are in different folders (agents/, utils/, etc.)
# Python needs to know WHERE to find these files when we try to import them

# Get the current file's directory (where streamlit_app.py is located)
current_dir = Path(__file__).parent
# __file__ is a special variable that contains the path to THIS file
# .parent goes up one level to get the folder containing this file

# Add the current directory to Python's search path
sys.path.insert(0, str(current_dir))
# sys.path is a list of folders where Python looks for modules
# insert(0, ...) adds our folder at the BEGINNING so it's checked first
# str() converts the Path object to a string (required by sys.path)

# ==============================================================================
# SECTION 3: IMPORT OUR CUSTOM MODULES
# ==============================================================================
# Now that Python knows where to look, we can import our own files

# Import the three main agents
from agents.supervisor_agent import SupervisorAgent  
# SupervisorAgent is the "manager" that decides which agent to use

from agents.knowledge_agent import KnowledgeAgent    
# KnowledgeAgent answers questions using RAG (Retrieval Augmented Generation)

from agents.marketing_agent import MarketingAgent    
# MarketingAgent creates marketing campaigns

# Import utility systems
from utils.cache_manager import ResponseCache        
# ResponseCache saves previous answers to avoid repeating work

from utils.memory_manager import ConversationMemory  
# ConversationMemory remembers the conversation history

from utils.observability import PerformanceMonitor   
# PerformanceMonitor tracks how fast/well the system is working

from utils.feedback_system import FeedbackCollector  
# FeedbackCollector saves user ratings and feedback

# Import configuration settings
from config import *  
# This imports ALL variables from config.py (API keys, model names, etc.)
# The * means "import everything"

# ==============================================================================
# SECTION 4: PAGE CONFIGURATION
# ==============================================================================
# This sets up the basic appearance and behavior of the web page

st.set_page_config(
    page_title="ICICI HFC AI Assistant - Multi-Agent Demo",  
    # Text shown in browser tab
    
    page_icon="🏠",  
    # Emoji shown in browser tab (house emoji for home loans)
    
    layout="wide",   
    # Use full width of screen (instead of narrow centered layout)
    
    initial_sidebar_state="expanded"  
    # Sidebar starts open (not collapsed)
)

# ==============================================================================
# SECTION 5: SESSION STATE INITIALIZATION
# ==============================================================================
# Session state is like the "memory" of your app across reruns
# Every time a user clicks a button, Streamlit reruns the ENTIRE script from top
# Session state helps us REMEMBER things between these reruns

# Why use session state?
# Example: If user types a query, we need to remember it when button is clicked
# Without session state, the query would be forgotten on rerun

# ==============================================================================
# AUTO-INITIALIZE CHROMADB (Streamlit Cloud Deployment Support)
# ==============================================================================

# def check_and_build_chromadb():
#     """
#     Check if ChromaDB exists. If not, build it automatically.
#     This ensures Streamlit Cloud deployment works without manual setup.
#     """
#     from pathlib import Path
#     import subprocess
    
#     chroma_path = Path(CHROMA_PERSIST_DIR)
    
#     # Check if database exists and has content
#     if chroma_path.exists() and any(chroma_path.iterdir()):
#         return True  # Database ready
    
#     # Database missing - build it
#     st.warning("⚠️ ChromaDB not found. Building vector database for first time...")
#     st.info("📚 This takes ~2 minutes on first deployment. Please wait...")
    
#     try:
#         with st.spinner("Indexing ICICI documents... (2 minutes)"):
#             # Run the indexing script
#             result = subprocess.run(
#                 ["python", "vectorstore/setup_chroma.py"],
#                 capture_output=True,
#                 text=True,
#                 timeout=300  # 5 minute timeout
#             )
            
#             if result.returncode == 0:
#                 st.success("✅ ChromaDB initialized successfully!")
#                 return True
#             else:
#                 st.error(f"❌ Build failed: {result.stderr}")
#                 st.code(result.stdout, language="text")
#                 return False
                
#     except subprocess.TimeoutExpired:
#         st.error("❌ Build timeout (>5 minutes). Check corpus size.")
#         return False
#     except Exception as e:
#         st.error(f"❌ Build error: {e}")
#         return False
def check_and_build_chromadb():
    """
    Check if ChromaDB exists. If not, build it automatically.
    This ensures Streamlit Cloud deployment works without manual setup.
    """
    from pathlib import Path
    
    chroma_path = Path(CHROMA_PERSIST_DIR)
    
    # Check if database exists and has content
    if chroma_path.exists():
        try:
            files = list(chroma_path.glob('**/*'))
            if len(files) > 5:  # Need at least a few DB files
                return True  # Database exists
        except:
            pass
    
    # Database missing - build it NOW
    st.warning("⚠️ ChromaDB not found. Building vector database...")
    st.info("📚 First-time setup: Indexing documents (~2 minutes)")
    
    try:
        with st.spinner("Building ChromaDB... Please wait..."):
            
            # Import required modules directly
            import sys
            import chromadb
            from chromadb.utils import embedding_functions
            
            # Add vectorstore to path
            vectorstore_path = Path(__file__).parent / "vectorstore"
            if str(vectorstore_path) not in sys.path:
                sys.path.insert(0, str(vectorstore_path))
            
            # Import document processor
            from vectorstore.document_processor import DocumentProcessor
            
            # Create ChromaDB client
            client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
            
            # Create embedding function
            embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=EMBEDDING_MODEL
            )
            
            # Delete collection if exists (fresh start)
            try:
                client.delete_collection(name=BANKING_COLLECTION)
            except:
                pass
            
            # Create new collection
            collection = client.create_collection(
                name=BANKING_COLLECTION,
                embedding_function=embedding_func,
                metadata={"description": "ICICI HFC Banking Products"}
            )
            
            # Process documents
            processor = DocumentProcessor()
            corpus_dir = Path(__file__).parent / "corpus"
            
            # Find all text files
            txt_files = list(corpus_dir.glob("*.txt"))
            
            if not txt_files:
                st.error(f"❌ No .txt files found in {corpus_dir}!")
                st.info(f"Expected path: {corpus_dir.absolute()}")
                return False
            
            # Process each file with progress
            total_chunks = 0
            progress_bar = st.progress(0)
            
            for idx, txt_file in enumerate(txt_files):
                st.text(f"Processing: {txt_file.name}")
                chunks = processor.process_pdf(txt_file)
                
                # Add to ChromaDB
                if chunks:
                    collection.add(
                        documents=[c['content'] for c in chunks],
                        metadatas=[c['metadata'] for c in chunks],
                        ids=[c['id'] for c in chunks]
                    )
                    total_chunks += len(chunks)
                
                # Update progress
                progress_bar.progress((idx + 1) / len(txt_files))
            
            st.success(f"✅ ChromaDB built! {total_chunks} chunks from {len(txt_files)} files")
            return True
                
    except Exception as e:
        st.error(f"❌ Build error: {str(e)}")
        import traceback
        st.code(traceback.format_exc(), language="python")
        return False


# Run ChromaDB check ONCE per session
if 'chromadb_ready' not in st.session_state:
    if check_and_build_chromadb():
        st.session_state.chromadb_ready = True
        st.rerun()  # Restart to load the new database
    else:
        st.error("Failed to initialize ChromaDB. Check logs and corpus/ folder.")
        st.stop()

# Now continue with existing supervisor initialization...



if 'supervisor' not in st.session_state:
    # Check if 'supervisor' key exists in session state
    # If NOT (first time running), initialize it
    
    st.session_state.supervisor = SupervisorAgent(
        # Create the supervisor agent instance
        # This is the main "brain" that routes queries to other agents
        
        enable_memory=True,      # Turn ON conversation memory
        enable_cache=True,       # Turn ON response caching
        enable_monitoring=True,  # Turn ON performance tracking
        enable_feedback=True     # Turn ON feedback collection
    )
    # Now st.session_state.supervisor exists and will persist across reruns

if 'query_history' not in st.session_state:
    # Initialize query history as empty list
    # This will store all queries made in this session
    st.session_state.query_history = []
    # [] creates an empty Python list to which we can append items later

if 'current_session_id' not in st.session_state:
    # Create a unique session ID for this user
    # This helps track conversations separately for different users
    
    st.session_state.current_session_id = f"session_{int(time.time())}"
    # f"..." is an f-string (formatted string) in Python
    # time.time() gives current time as a number (seconds since 1970)
    # int() converts it to integer (removes decimals)
    # Result: something like "session_1736920800"

if 'story_mode_active' not in st.session_state:
    # Track if the story demo is currently playing
    st.session_state.story_mode_active = False
    # Boolean (True/False) to control story playback

if 'story_step' not in st.session_state:
    # Track which step of the story we're on
    st.session_state.story_step = 0
    # Integer starting at 0 (first step)
    
    
# ⬇️⬇️⬇️ ADDED THIS NEW BLOCK HERE ⬇️⬇️⬇️ 
if 'selected_query' not in st.session_state:
    # Initialize selected query for the query interface
    # This prevents AttributeError when query_interface.py tries to access it
    st.session_state.selected_query = ''
    # Empty string as default value (no query selected initially)
# ⬆️⬆️⬆️ END OF NEW CODE ⬆️⬆️⬆️

# ==============================================================================
# SECTION 6: CUSTOM CSS STYLING
# ==============================================================================
# CSS (Cascading Style Sheets) controls how things LOOK on the webpage
# We inject custom CSS to make the app look professional

st.markdown("""
    <style>
    /* This is a CSS comment - it won't affect the code */
    
    /* Style for main title */
    .main-title {
        font-size: 2.5rem;        /* rem is a size unit, 2.5rem = 2.5 times base font */
        font-weight: bold;         /* Makes text thick/bold */
        color: #1f77b4;            /* Hex color code for blue */
        text-align: center;        /* Center the text horizontally */
        margin-bottom: 1rem;       /* Space below the title */
    }
    
    /* Style for metric cards (those boxes showing numbers) */
    .metric-card {
        background-color: #f0f2f6;  /* Light gray background */
        padding: 1.5rem;            /* Space inside the box (all sides) */
        border-radius: 10px;        /* Rounded corners (10px curve) */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);  /* Subtle shadow for depth */
        /* rgba(0,0,0,0.1) = black color with 10% opacity (transparency) */
        margin-bottom: 1rem;        /* Space below each card */
    }
    
    /* Style for agent status indicators */
    .agent-active {
        background-color: #90EE90;  /* Light green when agent is active */
        border: 2px solid #228B22;  /* Dark green border */
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .agent-inactive {
        background-color: #D3D3D3;  /* Gray when agent is not active */
        border: 2px solid #808080;  /* Darker gray border */
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Style for success messages */
    .success-box {
        background-color: #d4edda;  /* Light green background */
        border-left: 4px solid #28a745;  /* Green left border (thick) */
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;             /* Margin top and bottom (1rem each) */
    }
    
    /* Style for info boxes */
    .info-box {
        background-color: #d1ecf1;  /* Light blue background */
        border-left: 4px solid #17a2b8;  /* Blue left border */
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    </style>
""", unsafe_allow_html=True)
# unsafe_allow_html=True allows us to inject HTML/CSS code
# Normally Streamlit blocks HTML for security, this overrides that

# ==============================================================================
# SECTION 7: MAIN TITLE AND HEADER
# ==============================================================================

# Display the main title using our custom CSS class
st.markdown('<h1 class="main-title">🏠 ICICI HFC AI Assistant - Multi-Agent System</h1>', 
            unsafe_allow_html=True)
# <h1> is HTML for "heading level 1" (largest heading)
# class="main-title" applies our CSS styling from above

# Subtitle with description
st.markdown("""
    <div style="text-align: center; color: #666; margin-bottom: 2rem;">
        Powered by RAG (Retrieval Augmented Generation) + Multi-Agent Architecture
    </div>
""", unsafe_allow_html=True)
# <div> is a container element in HTML
# style="..." applies CSS directly (inline styling)
# #666 is a gray color (shorthand for #666666)

# Horizontal line separator
st.markdown("---")
# In Streamlit, "---" creates a horizontal line (divider)

# ==============================================================================
# SECTION 8: SIDEBAR NAVIGATION
# ==============================================================================
# Sidebar is the panel on the left side of the screen
# We use it for navigation and settings

with st.sidebar:
    # Everything indented under "with st.sidebar:" will appear in the sidebar
    
    # Sidebar title
    st.header("📱 Navigation")
    # st.header() creates a medium-sized heading
    
    # Tab selection using radio buttons
    selected_tab = st.radio(
        # st.radio creates a set of radio buttons (only one can be selected)
        
        "Select View:",  
        # Label text shown above the radio buttons
        
        ["💬 Query Interface", "🎬 Story Demo", "📊 Analytics Dashboard"],
        # List of options for the radio buttons
        # Each string becomes one radio button option
        
        index=0  
        # Which option is selected by default (0 = first option)
    )
    
    # Divider line in sidebar
    st.markdown("---")
    
    # System status section
    st.subheader("⚙️ System Status")
    # st.subheader() creates a smaller heading than st.header()
    
    # Check if supervisor agent is loaded
    if st.session_state.supervisor:
        # If supervisor exists in session state (it should, we initialized it above)
        
        st.success("✅ Supervisor Agent: Active")
        # st.success() shows a green success message box
        
        # Show which features are enabled
        st.info(f"""
            **Enabled Features:**
            - 💾 Memory: {st.session_state.supervisor.enable_memory}
            - 🗂️ Cache: {st.session_state.supervisor.enable_cache}
            - 📊 Monitoring: {st.session_state.supervisor.enable_monitoring}
            - 👍 Feedback: {st.session_state.supervisor.enable_feedback}
        """)
        # st.info() shows a blue info message box
        # f"..." is f-string allowing us to insert variables with {variable}
        # Result: True/False values will be shown for each feature
    else:
        # If supervisor doesn't exist (shouldn't happen, but good to check)
        st.error("❌ Supervisor Agent: Not Loaded")
        # st.error() shows a red error message box
    
    # Another divider
    st.markdown("---")
    
    # Current session info
    st.subheader("📝 Session Info")
    
    # Display session ID
    st.text(f"Session: {st.session_state.current_session_id}")
    # st.text() displays plain text (no formatting)
    
    # Display query count
    st.metric("Queries This Session", len(st.session_state.query_history))
    # st.metric() shows a number in a nice formatted box
    # len() gives the length (number of items) in the query_history list

# ==============================================================================
# SECTION 9: TAB ROUTING LOGIC
# ==============================================================================
# Based on which radio button was selected, show different content

if selected_tab == "💬 Query Interface":
    # User selected the Query Interface tab
    # We'll import and run the query interface component
    
    from components.query_interface import render_query_interface
    # Import the function that creates the query interface
    # This function is defined in components/query_interface.py (we'll create this next)
    
    render_query_interface(st.session_state.supervisor, st.session_state.current_session_id)
    # Call the function and pass:
    # 1. supervisor agent (to process queries)
    # 2. session_id (to track this conversation)

elif selected_tab == "🎬 Story Demo":
    # User selected the Story Demo tab
    
    from components.storyboard import render_storyboard
    # Import the storyboard rendering function
    
    render_storyboard(st.session_state.supervisor)
    # Call it with supervisor agent

elif selected_tab == "📊 Analytics Dashboard":
    # User selected the Analytics Dashboard tab
    
    from components.dashboard import render_dashboard
    # Import the dashboard rendering function
    
    render_dashboard(st.session_state.supervisor)
    # Call it with supervisor agent (to get metrics from it)

# ==============================================================================
# SECTION 10: FOOTER
# ==============================================================================

st.markdown("---")  # Divider line

# Footer with app information
st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem; font-size: 0.9rem;">
        <p><b>ICICI Home Finance Corporation - AI Assistant Demo</b></p>
        <p>Built with Streamlit, ChromaDB, Groq LLM, and LangChain</p>
        <p>Multi-Agent Architecture with RAG Pipeline</p>
    </div>
""", unsafe_allow_html=True)
# <p> is HTML paragraph tag
# <b> makes text bold
# 0.9rem makes font slightly smaller than normal

# ==============================================================================
# END OF MAIN APPLICATION FILE
# ==============================================================================
# This file sets up the structure and navigation
# The actual functionality for each tab is in separate component files
# This keeps code organized and easier to maintain
# ==============================================================================