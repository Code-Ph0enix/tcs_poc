"""
==============================================================================
ANALYTICS DASHBOARD COMPONENT - OBSERVABILITY & METRICS VISUALIZATION
==============================================================================

Purpose: This file creates the "Analytics Dashboard" tab that shows real-time
         metrics and system performance data. It's like a "control panel" that
         shows how well your AI system is working.

Location: tcs_poc/components/dashboard.py

Called by: streamlit_app.py when "Analytics Dashboard" tab is selected

What it shows:
- Performance metrics (response times, query counts)
- Agent usage statistics
- User feedback analytics
- Cache efficiency metrics
- Memory/conversation stats
- Live query log
- System health indicators
- Anomaly detection

Think of this as the "cockpit dashboard" of an airplane - all vital stats
displayed clearly so you can monitor system health.

==============================================================================
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import streamlit as st  # For web UI
import pandas as pd  # For data manipulation and tables
# pandas is like Excel for Python - works with rows and columns of data
import plotly.express as px  # For interactive charts
# plotly creates beautiful, interactive charts users can hover over
import plotly.graph_objects as go  # For custom chart layouts
from datetime import datetime, timedelta  # For working with dates/times
import json  # For reading JSON files
from pathlib import Path  # For file path handling
from typing import Dict, List, Any, Optional  # Type hints
import os  # For checking file existence
import time  # For timestamps

# ==============================================================================
# HELPER FUNCTIONS FOR DATA COLLECTION
# ==============================================================================

def get_performance_metrics(supervisor_agent) -> Dict[str, Any]:
    """
    Collects performance metrics from the observability system.
    
    Parameters:
    -----------
    supervisor_agent : SupervisorAgent
        The supervisor instance that has the performance monitor
        
    Returns:
    --------
    dict
        Dictionary containing all performance statistics like:
        {
            'total_queries': 127,
            'success_rate': 98.4,
            'avg_response_time': 1.8,
            'by_agent': {...},
            ...
        }
    
    How it works:
    -------------
    The supervisor agent has a PerformanceMonitor object that tracks all queries.
    We call its get_stats() method to retrieve aggregated statistics.
    
    If monitoring is disabled, we return dummy/default values.
    """
    
    if supervisor_agent.enable_monitoring:
        # If monitoring is enabled, get real stats
        
        try:
            stats = supervisor_agent.monitor.get_stats()
            # Call get_stats() method from observability.py
            # This returns a dictionary with all metrics
            
            return stats
            # Return the stats dictionary
            
        except Exception as e:
            # If any error occurs (file not found, etc.)
            
            st.warning(f"⚠️ Could not load performance metrics: {str(e)}")
            # Show warning to user
            
            # Return default empty stats
            return {
                'total_queries': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'by_agent': {}
            }
    else:
        # Monitoring is disabled
        st.info("ℹ️ Performance monitoring is disabled. Enable it in supervisor initialization.")
        
        return {
            'total_queries': 0,
            'success_rate': 0.0,
            'avg_response_time': 0.0,
            'by_agent': {}
        }

def get_cache_stats(supervisor_agent) -> Dict[str, Any]:
    """
    Collects cache efficiency statistics.
    
    Parameters:
    -----------
    supervisor_agent : SupervisorAgent
        The supervisor with cache manager
        
    Returns:
    --------
    dict
        Cache statistics including hit rate, total entries, etc.
    
    Example return:
    {
        'total_entries': 45,
        'hit_rate': 34.5,  # percentage
        'miss_rate': 65.5,
        'total_hits': 28,
        'total_misses': 53
    }
    """
    
    if supervisor_agent.enable_cache:
        # Cache is enabled
        
        try:
            stats = supervisor_agent.cache.get_stats()
            # Call get_stats() from cache_manager.py
            
            return stats
            
        except Exception as e:
            st.warning(f"⚠️ Could not load cache stats: {str(e)}")
            return {
                'total_entries': 0,
                'hit_rate': 0.0,
                'miss_rate': 0.0,
                'total_hits': 0,
                'total_misses': 0
            }
    else:
        st.info("ℹ️ Cache is disabled.")
        return {
            'total_entries': 0,
            'hit_rate': 0.0,
            'miss_rate': 0.0,
            'total_hits': 0,
            'total_misses': 0
        }

def get_feedback_stats(supervisor_agent) -> Dict[str, Any]:
    """
    Collects user feedback and satisfaction metrics.
    
    Parameters:
    -----------
    supervisor_agent : SupervisorAgent
        
    Returns:
    --------
    dict
        Feedback statistics including ratings, satisfaction rate, etc.
    
    Example:
    {
        'total_feedbacks': 93,
        'avg_rating': 4.3,
        'satisfaction_rate': 78.5,  # percentage
        'thumbs_up': 73,
        'thumbs_down': 20,
        'by_agent': {...}
    }
    """
    
    if supervisor_agent.enable_feedback:
        try:
            stats = supervisor_agent.feedback.get_feedback_stats()
            # Call from feedback_system.py
            
            return stats
            
        except Exception as e:
            st.warning(f"⚠️ Could not load feedback stats: {str(e)}")
            return {
                'total_feedbacks': 0,
                'avg_rating': 0.0,
                'satisfaction_rate': 0.0,
                'thumbs_up': 0,
                'thumbs_down': 0,
                'by_agent': {}
            }
    else:
        st.info("ℹ️ Feedback collection is disabled.")
        return {
            'total_feedbacks': 0,
            'avg_rating': 0.0,
            'satisfaction_rate': 0.0,
            'thumbs_up': 0,
            'thumbs_down': 0,
            'by_agent': {}
        }

def get_memory_stats(supervisor_agent) -> Dict[str, Any]:
    """
    Collects conversation memory statistics.
    
    Returns info about how many sessions are active, total exchanges, etc.
    
    Returns:
    --------
    dict
        Memory statistics
    """
    
    if supervisor_agent.enable_memory:
        try:
            # Memory manager doesn't have a built-in get_stats() method
            # So we'll create stats by checking the memory directory
            
            memory_dir = Path('./memory')
            # Path to memory folder
            
            if memory_dir.exists():
                # If folder exists
                
                session_files = list(memory_dir.glob('*.json'))
                # Get all .json files in the directory
                # .glob('*.json') finds all files ending with .json
                # list() converts the result to a Python list
                
                total_sessions = len(session_files)
                # Count how many session files exist
                
                total_exchanges = 0
                # Initialize counter for exchanges
                
                # Loop through each session file to count exchanges
                for session_file in session_files:
                    try:
                        with open(session_file, 'r') as f:
                            # Open file for reading
                            session_data = json.load(f)
                            # Parse JSON file into Python dictionary
                            
                            if 'history' in session_data:
                                total_exchanges += len(session_data['history'])
                                # Count exchanges in this session
                    except:
                        # If file is corrupted or unreadable, skip it
                        continue
                
                # Calculate average
                avg_exchanges = total_exchanges / total_sessions if total_sessions > 0 else 0
                # Divide total by count (avoid division by zero)
                
                return {
                    'active_sessions': total_sessions,
                    'total_exchanges': total_exchanges,
                    'avg_exchanges_per_session': round(avg_exchanges, 1)
                    # round(x, 1) rounds to 1 decimal place
                }
            else:
                # Memory directory doesn't exist yet
                return {
                    'active_sessions': 0,
                    'total_exchanges': 0,
                    'avg_exchanges_per_session': 0
                }
                
        except Exception as e:
            st.warning(f"⚠️ Could not load memory stats: {str(e)}")
            return {
                'active_sessions': 0,
                'total_exchanges': 0,
                'avg_exchanges_per_session': 0
            }
    else:
        st.info("ℹ️ Memory is disabled.")
        return {
            'active_sessions': 0,
            'total_exchanges': 0,
            'avg_exchanges_per_session': 0
        }

def load_recent_queries(limit: int = 10) -> List[Dict]:
    """
    Loads the most recent queries from the observability logs.
    
    Parameters:
    -----------
    limit : int
        How many recent queries to load (default: 10)
        
    Returns:
    --------
    list of dict
        List of recent query dictionaries, newest first
        
    How it works:
    -------------
    Reads the latest log file from ./logs/ directory and returns last N queries.
    """
    
    logs_dir = Path('./logs')
    # Path to logs directory
    
    if not logs_dir.exists():
        # If logs folder doesn't exist
        return []
        # Return empty list
    
    # Find the most recent log file
    # Log files are named like: queries_20260115.jsonl
    
    log_files = sorted(logs_dir.glob('queries_*.jsonl'), reverse=True)
    # Get all query log files and sort by name (newest first)
    # reverse=True makes it descending order
    
    if not log_files:
        # No log files found
        return []
    
    recent_file = log_files[0]
    # Take the first (most recent) file
    
    queries = []
    # Initialize empty list to store queries
    
    try:
        with open(recent_file, 'r') as f:
            # Open file for reading
            
            for line in f:
                # Read line by line (.jsonl = JSON Lines format)
                # Each line is a separate JSON object
                
                try:
                    query_data = json.loads(line)
                    # Parse JSON string to dictionary
                    
                    queries.append(query_data)
                    # Add to our list
                    
                except:
                    # Skip malformed lines
                    continue
        
        # Return last N queries (most recent)
        return queries[-limit:]
        # [-limit:] takes last 'limit' items
        # For limit=10, gets last 10 items
        
    except Exception as e:
        st.warning(f"⚠️ Could not load recent queries: {str(e)}")
        return []

# ==============================================================================
# MAIN RENDERING FUNCTION
# ==============================================================================

def render_dashboard(supervisor_agent):
    """
    Main function that renders the complete analytics dashboard.
    
    This creates multiple panels showing different aspects of system performance.
    
    Parameters:
    -----------
    supervisor_agent : SupervisorAgent
        The supervisor instance to get metrics from
    """
    
    # ==========================================================================
    # PAGE HEADER
    # ==========================================================================
    
    st.title("📊 Analytics Dashboard - System Observability")
    
    st.markdown("""
        Real-time metrics and performance analytics for the multi-agent AI system.
        Monitor query performance, cache efficiency, user satisfaction, and system health.
    """)
    
    st.markdown("---")
    
    # ==========================================================================
    # REFRESH BUTTON
    # ==========================================================================
    
    col1, col2, col3 = st.columns([1, 1, 4])
    # Create 3 columns with custom widths
    # [1, 1, 4] means: first two are equal, third is 4x wider
    
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            # Button to reload all metrics
            st.rerun()
            # Rerun the script to fetch fresh data
    
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=False)
        # Checkbox for auto-refresh (future enhancement)
    
    st.markdown("---")
    
    # ==========================================================================
    # COLLECT ALL METRICS
    # ==========================================================================
    # Before displaying, gather all the data we need
    
    with st.spinner("📊 Loading dashboard metrics..."):
        # Show spinner while collecting data
        
        perf_stats = get_performance_metrics(supervisor_agent)
        cache_stats = get_cache_stats(supervisor_agent)
        feedback_stats = get_feedback_stats(supervisor_agent)
        memory_stats = get_memory_stats(supervisor_agent)
        recent_queries = load_recent_queries(limit=10)
    
    # ==========================================================================
    # SECTION 1: KEY METRICS OVERVIEW (Top Cards)
    # ==========================================================================
    
    st.subheader("🎯 Key Performance Indicators")
    
    # Create 5 columns for KPI cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Queries",
            value=perf_stats.get('total_queries', 0),
            delta=None,  # Could show change from yesterday if we track historical data
            help="Total number of queries processed"
        )
        # st.metric creates a nice card with big number
    
    with col2:
        success_rate = perf_stats.get('success_rate', 0.0)
        st.metric(
            label="Success Rate",
            value=f"{success_rate:.1f}%",
            # :.1f formats as decimal with 1 place (like 98.5)
            delta=None,
            help="Percentage of queries that completed successfully"
        )
    
    with col3:
        avg_time = perf_stats.get('avg_response_time', 0.0)
        st.metric(
            label="Avg Response Time",
            value=f"{avg_time:.2f}s",
            delta=None,
            help="Average time to respond to queries"
        )
    
    with col4:
        avg_rating = feedback_stats.get('avg_rating', 0.0)
        # Create star emoji visualization
        stars = "⭐" * int(avg_rating)  # Repeat star emoji
        # int(4.3) = 4, so "⭐⭐⭐⭐"
        
        st.metric(
            label="User Rating",
            value=f"{avg_rating:.1f}/5",
            delta=None,
            help=f"Average user satisfaction rating {stars}"
        )
    
    with col5:
        cache_hit_rate = cache_stats.get('hit_rate', 0.0)
        st.metric(
            label="Cache Hit Rate",
            value=f"{cache_hit_rate:.1f}%",
            delta=None,
            help="Percentage of queries served from cache"
        )
    
    st.markdown("---")
    
    # ==========================================================================
    # SECTION 2: AGENT PERFORMANCE COMPARISON
    # ==========================================================================
    
    st.subheader("🤖 Agent Performance Analytics")
    
    # Get agent breakdown from performance stats
    by_agent = perf_stats.get('by_agent', {})
    # This is a dictionary like:
    # {
    #     'knowledge': {'count': 85, 'avg_time': 2.1, 'success_rate': 99},
    #     'marketing': {'count': 42, 'avg_time': 1.4, 'success_rate': 97}
    # }
    
    if by_agent:
        # If we have agent data
        
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Chart 1: Query count by agent (Bar chart)
            st.markdown("#### Query Distribution by Agent")
            
            # Prepare data for chart
            agent_names = list(by_agent.keys())
            # Get agent names: ['knowledge', 'marketing']
            
            query_counts = [by_agent[agent]['count'] for agent in agent_names]
            # Get counts: [85, 42]
            # List comprehension - loops through agents and gets count for each
            
            # Create DataFrame for plotly
            df_agents = pd.DataFrame({
                'Agent': agent_names,
                'Queries': query_counts
            })
            # pandas DataFrame is like a table:
            # | Agent      | Queries |
            # |------------|---------|
            # | knowledge  | 85      |
            # | marketing  | 42      |
            
            # Create bar chart using plotly
            fig = px.bar(
                df_agents,  # Data source
                x='Agent',  # X-axis: agent names
                y='Queries',  # Y-axis: query counts
                color='Agent',  # Color bars by agent
                title="Queries Handled by Each Agent",
                color_discrete_map={
                    # Custom colors for each agent
                    'knowledge': '#1f77b4',  # Blue
                    'marketing': '#ff7f0e',  # Orange
                    'cached': '#2ca02c'      # Green
                }
            )
            # px.bar creates an interactive bar chart
            
            # Update chart layout
            fig.update_layout(
                showlegend=False,  # Hide legend (obvious from x-axis)
                height=300  # Chart height in pixels
            )
            
            st.plotly_chart(fig, use_container_width=True)
            # Display the chart, stretching to container width
        
        with col2:
            # Chart 2: Average response time by agent
            st.markdown("#### Average Response Time by Agent")
            
            avg_times = [by_agent[agent]['avg_time'] for agent in agent_names]
            # Get average times: [2.1, 1.4]
            
            df_times = pd.DataFrame({
                'Agent': agent_names,
                'Avg Time (s)': avg_times
            })
            
            fig = px.bar(
                df_times,
                x='Agent',
                y='Avg Time (s)',
                color='Agent',
                title="Response Time Comparison",
                color_discrete_map={
                    'knowledge': '#1f77b4',
                    'marketing': '#ff7f0e',
                    'cached': '#2ca02c'
                }
            )
            
            fig.update_layout(
                showlegend=False,
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Agent stats table
        st.markdown("#### Detailed Agent Statistics")
        
        # Create a formatted table
        table_data = []
        # Empty list to store rows
        
        for agent, stats in by_agent.items():
            # Loop through each agent's stats
            
            table_data.append({
                'Agent': agent.capitalize(),  # 'knowledge' → 'Knowledge'
                'Total Queries': stats['count'],
                'Avg Response Time': f"{stats['avg_time']:.2f}s",
                'Success Rate': f"{stats.get('success_rate', 0):.1f}%"
            })
        
        df_table = pd.DataFrame(table_data)
        # Convert list of dicts to DataFrame
        
        st.dataframe(df_table, use_container_width=True, hide_index=True)
        # st.dataframe(df_table, width='stretch', hide_index=True)
        # st.dataframe displays an interactive table
        # hide_index=True hides the row numbers
    
    else:
        # No agent data available
        st.info("📊 No agent performance data available yet. Process some queries to see analytics.")
    
    st.markdown("---")
    
    # ==========================================================================
    # SECTION 3: USER FEEDBACK ANALYTICS
    # ==========================================================================
    
    st.subheader("👍 User Feedback & Satisfaction")
    
    total_feedback = feedback_stats.get('total_feedbacks', 0)
    
    if total_feedback > 0:
        # We have feedback data
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Satisfaction metrics
            st.markdown("#### Satisfaction Metrics")
            
            satisfaction_rate = feedback_stats.get('satisfaction_rate', 0.0)
            thumbs_up = feedback_stats.get('thumbs_up', 0)
            thumbs_down = feedback_stats.get('thumbs_down', 0)
            
            # Display metrics in columns
            subcol1, subcol2, subcol3 = st.columns(3)
            
            with subcol1:
                st.metric("Satisfaction", f"{satisfaction_rate:.1f}%")
            with subcol2:
                st.metric("👍 Positive", thumbs_up)
            with subcol3:
                st.metric("👎 Negative", thumbs_down)
            
            # Pie chart: Thumbs up vs down
            fig = go.Figure(data=[go.Pie(
                labels=['Positive 👍', 'Negative 👎'],
                values=[thumbs_up, thumbs_down],
                marker=dict(colors=['#2ca02c', '#d62728'])
                # Green for positive, red for negative
            )])
            
            fig.update_layout(
                title="Feedback Distribution",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Rating distribution
            st.markdown("#### Rating Distribution")
            
            # For now, show average rating prominently
            avg_rating = feedback_stats.get('avg_rating', 0.0)
            
            # Create a star rating visualization
            stars_filled = int(avg_rating)  # Full stars
            has_half = (avg_rating - stars_filled) >= 0.5  # Half star?
            
            star_display = "⭐" * stars_filled
            if has_half:
                star_display += "⭐"  # Could use half-star emoji
            
            st.markdown(f"### {star_display}")
            st.markdown(f"**Average: {avg_rating:.2f} / 5.0**")
            st.markdown(f"Based on {total_feedback} ratings")
            
            # If we have feedback by agent
            feedback_by_agent = feedback_stats.get('by_agent', {})
            
            if feedback_by_agent:
                st.markdown("**Ratings by Agent:**")
                
                for agent, agent_fb in feedback_by_agent.items():
                    agent_rating = agent_fb.get('avg_rating', 0)
                    agent_count = agent_fb.get('count', 0)
                    
                    st.markdown(f"- **{agent.capitalize()}**: {agent_rating:.1f}/5 ({agent_count} ratings)")
        
        # Show recent negative feedback for improvement
        st.markdown("#### 📉 Areas for Improvement")
        
        try:
            negative_feedback = supervisor_agent.feedback.get_negative_feedback(limit=3)
            # Get up to 3 recent negative feedbacks
            
            if negative_feedback:
                for idx, fb in enumerate(negative_feedback, 1):
                    with st.expander(f"Feedback {idx}: Rating {fb['rating']}/5"):
                        st.write(f"**Query:** {fb['query']}")
                        st.write(f"**Comment:** {fb.get('comment', 'No comment')}")
                        st.write(f"**Agent:** {fb['agent_type']}")
            else:
                st.success("✅ No negative feedback! All users are satisfied.")
        except:
            st.info("Negative feedback data not available.")
    
    else:
        st.info("📊 No user feedback collected yet. Users need to rate responses.")
    
    st.markdown("---")
    
    # ==========================================================================
    # SECTION 4: CACHE EFFICIENCY
    # ==========================================================================
    
    st.subheader("💾 Cache Performance")
    
    total_entries = cache_stats.get('total_entries', 0)
    
    if total_entries > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Cache metrics
            st.markdown("#### Cache Statistics")
            
            subcol1, subcol2 = st.columns(2)
            
            with subcol1:
                st.metric("Total Entries", total_entries)
                st.metric("Cache Hits", cache_stats.get('total_hits', 0))
            
            with subcol2:
                st.metric("Hit Rate", f"{cache_stats.get('hit_rate', 0):.1f}%")
                st.metric("Cache Misses", cache_stats.get('total_misses', 0))
        
        with col2:
            # Pie chart: Hit vs Miss
            st.markdown("#### Hit/Miss Ratio")
            
            hits = cache_stats.get('total_hits', 0)
            misses = cache_stats.get('total_misses', 0)
            
            fig = go.Figure(data=[go.Pie(
                labels=['Cache Hit ✓', 'Cache Miss ✗'],
                values=[hits, misses],
                marker=dict(colors=['#2ca02c', '#ff7f0e'])
            )])
            
            fig.update_layout(height=300)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Explain cache benefits
        st.markdown("#### 💡 Cache Benefits")
        
        avg_llm_time = 2.5  # Typical LLM response time
        avg_cache_time = 0.1  # Cache response time
        
        time_saved = hits * (avg_llm_time - avg_cache_time)
        # Calculate total time saved by cache
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Time Saved", f"{time_saved:.1f}s", 
                     help="Total time saved by serving cached responses")
        
        with col2:
            speedup = avg_llm_time / avg_cache_time if avg_cache_time > 0 else 0
            st.metric("Speedup Factor", f"{speedup:.0f}x",
                     help="How much faster cached responses are")
        
        with col3:
            # Estimate cost savings (assuming $0.002 per LLM call)
            cost_saved = hits * 0.002
            st.metric("Est. Cost Saved", f"${cost_saved:.3f}",
                     help="Estimated API cost savings from cache")
    
    else:
        st.info("📊 No cache data yet. Cache will populate as queries are processed.")
    
    st.markdown("---")
    
    # ==========================================================================
    # SECTION 5: MEMORY & CONVERSATION ANALYTICS
    # ==========================================================================
    
    st.subheader("🧠 Memory & Conversation Analytics")
    
    active_sessions = memory_stats.get('active_sessions', 0)
    
    if active_sessions > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Sessions", active_sessions,
                     help="Number of ongoing conversation sessions")
        
        with col2:
            st.metric("Total Exchanges", memory_stats.get('total_exchanges', 0),
                     help="Total user-AI exchanges across all sessions")
        
        with col3:
            st.metric("Avg Exchanges/Session", 
                     memory_stats.get('avg_exchanges_per_session', 0),
                     help="Average conversation length")
    else:
        st.info("📊 No conversation memory data yet.")
    
    st.markdown("---")
    
    # # ==========================================================================
    # # SECTION 6: LIVE QUERY LOG
    # # ==========================================================================
    
    # st.subheader("📝 Recent Query Activity")
    
    # if recent_queries:
    #     # We have recent query data
        
    #     st.markdown(f"Showing last {len(recent_queries)} queries")
        
    #     # Create a table from recent queries
    #     log_data = []
        
    #     for query in reversed(recent_queries):
    #         # Reverse to show newest first
            
    #         # Parse timestamp
    #         timestamp = query.get('timestamp', time.time())
    #         dt = datetime.fromtimestamp(timestamp)
    #         time_str = dt.strftime('%I:%M:%S %p')
    #         # Format as "02:30:45 PM"
            
    #         log_data.append({
    #             'Time': time_str,
    #             'Query': query.get('query', 'N/A')[:50] + '...',  # Truncate long queries
    #             'Agent': query.get('agent_type', 'unknown').capitalize(),
    #             'Response Time': f"{query.get('response_time', 0):.2f}s",
    #             'Status': '✅' if query.get('success', True) else '❌'
    #         })
        
    #     df_log = pd.DataFrame(log_data)
        
    #     st.dataframe(df_log, use_container_width=True, hide_index=True)
    #     # st.dataframe(df_table, width='stretch', hide_index=True)
        
    # else:
    #     st.info("📊 No recent query logs available yet.")
    
    # st.markdown("---")
    
    
    
    # ==========================================================================
    # SECTION 6: LIVE QUERY LOG
    # ==========================================================================

    st.subheader("📝 Recent Query Activity")

    if recent_queries:
    # We have recent query data
    
        st.markdown(f"Showing last {len(recent_queries)} queries")
    
    # Create a table from recent queries
        log_data = []
    
        for query in reversed(recent_queries):
        # Reverse to show newest first
        
        # Parse timestamp (FIX: Handle both string and numeric timestamps)
            timestamp = query.get('timestamp', time.time())
        # Get timestamp from query data
        
            try:
            # Try to convert timestamp to datetime
            # Handle different timestamp formats
            
                if isinstance(timestamp, str):
                # If timestamp is a string, try to parse it
                
                # Check if it's an ISO format string like "2026-01-15T12:30:45"
                    if 'T' in timestamp or '-' in timestamp:
                    # ISO format
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    # fromisoformat parses ISO strings
                    # .replace('Z', '+00:00') handles timezone indicator
                    else:
                    # It's a numeric timestamp stored as string
                        dt = datetime.fromtimestamp(float(timestamp))
                    # Convert string to float, then to datetime
            
                elif isinstance(timestamp, (int, float)):
                # If timestamp is already a number
                    dt = datetime.fromtimestamp(timestamp)
                # Direct conversion
            
                else:
                # Unknown format, use current time
                    dt = datetime.now()
            
                date_str = dt.strftime('%d %b %Y')  # "15 Jan 2026"
                time_str = dt.strftime('%I:%M:%S %p')
            # Format as "02:30:45 PM"
            
            except (ValueError, TypeError, OSError) as e:
            # If any error occurs in timestamp conversion, use "Unknown"
                date_str = "Unknown"
                time_str = "Unknown"
            # Fallback to avoid crashing
        
        # Build the log entry
            log_data.append({
                'Date': date_str,
                'Time': time_str,
                'Query': query.get('query', 'N/A')[:50] + '...',  # Truncate long queries
                'Agent': query.get('agent_type', 'unknown').capitalize(),
                'Response Time': f"{query.get('response_time', 0):.2f}s",
                'Status': '✅' if query.get('success', True) else '❌'
            })
    
        df_log = pd.DataFrame(log_data)
    
    # FIX: Updated parameter name for Streamlit 1.31+
        st.dataframe(df_log, width='stretch', hide_index=True)
    # Changed from use_container_width=True to width='stretch'
    
    else:
        st.info("📊 No recent query logs available yet.")

    st.markdown("---")

    
    # ==========================================================================
    # SECTION 7: SYSTEM HEALTH
    # ==========================================================================
    
    st.subheader("🏥 System Health Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Check if ChromaDB is accessible
        # st.markdown("#### ChromaDB")
        # try:
        #     # Try to check ChromaDB
        #     # This is a simplified check
        #     if Path('./chroma_db').exists():
        #         st.success("✅ Connected")
        #         # Count documents (simplified)
        #         st.caption("Database operational")
        #     else:
        #         st.error("❌ Not Found")
        # except:
        #     st.warning("⚠️ Cannot verify")
        # Check if ChromaDB is accessible
        st.markdown("#### ChromaDB")
        try:
    # Check multiple possible paths for ChromaDB
            chroma_paths = [
                Path('./chroma_db'),              # Root level
                Path('./vectorstore/chroma_db'),  # Inside vectorstore folder
                Path('../chroma_db')              # One level up
            ]
    
            found = False
            for path in chroma_paths:
                if path.exists():
                    found = True
                    st.success("✅ Connected")
                    st.caption(f"Found at: {path}")
            
            # Try to count files inside
                    try:
                        db_files = list(path.glob('**/*'))
                        st.caption(f"{len(db_files)} files")
                    except:
                        pass
                    break
    
            if not found:
                st.error("❌ Not Found")
                st.caption("Run: python vectorstore/setup_chroma.py")

        except Exception as e:
            st.warning("⚠️ Cannot verify")
            st.caption(f"Error: {str(e)}")

    
    with col2:
        # Check cache system
        st.markdown("#### Cache System")
        if supervisor_agent.enable_cache:
            st.success("✅ Active")
            st.caption(f"{total_entries} entries")
        else:
            st.warning("⚠️ Disabled")
    
    with col3:
        # Check monitoring
        st.markdown("#### Monitoring")
        if supervisor_agent.enable_monitoring:
            st.success("✅ Active")
            st.caption("Logging queries")
        else:
            st.warning("⚠️ Disabled")
    
    # Anomaly detection (if available)
    if supervisor_agent.enable_monitoring:
        st.markdown("#### ⚠️ Anomaly Detection")
        
        try:
            anomalies = supervisor_agent.monitor.detect_anomalies()
            # Call detect_anomalies from observability.py
            
            if anomalies:
                st.warning(f"⚠️ {len(anomalies)} anomalies detected")
                
                for anomaly in anomalies[:3]:  # Show first 3
                    with st.expander(f"{anomaly['type']}"):
                        st.json(anomaly)
            else:
                st.success("✅ No anomalies detected. System operating normally.")
        except:
            st.info("Anomaly detection not available.")

# ==============================================================================
# END OF DASHBOARD COMPONENT
# ==============================================================================
