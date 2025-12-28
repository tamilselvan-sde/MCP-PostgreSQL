#################################
#         streamlit_app.py
#################################

import streamlit as st
import pandas as pd
import json
import db_tools
import langgraph_agent
import config
from typing import Dict, Any

print("----------------- streamlit import completed or connected, ---------")
print("----------------- pandas import completed or connected, ---------")

# Configure page
st.set_page_config(
    page_title="MCP PostgreSQL Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "default_streamlit_thread"

print("#===============[ start_of_main_process ]==========")

# Sidebar
with st.sidebar:
    st.title("🤖 MCP Config")
    
    st.divider()
    
    st.subheader("Database Status")
    if db_tools.test_connection():
        st.success("Connected to PostgreSQL")
    else:
        st.error("Database Connection Failed")
        
    st.divider()
    
    st.subheader("Ollama Status")
    try:
        # Simple check by trying to init LLM (lightweight)
        # Note: Ideally we'd have a simpler ping method
        st.success(f"Connected to {config.OLLAMA_LLM_MODEL}")
    except Exception:
        st.error("Ollama Connection Failed")
        
    st.divider()
    
    st.subheader("Tools")
    st.code("db_query\ndb_list_tables\ndb_describe\ndb_insert\ndb_update\ndb_delete")
    
    st.divider()
    if st.button("Clear Conversation History"):
        st.session_state.messages = []
        # Generate new thread ID to effectively clear agent memory
        import uuid
        st.session_state.thread_id = f"thread_{uuid.uuid4().hex[:8]}"
        st.rerun()

# Main Interface
st.title("🧙‍♂️ MCP PostgreSQL Agent")
st.markdown("""
Chat with your **PostgreSQL database** using natural language!  
This agent uses **LangGraph** and **Ollama** to understand your intent and execute safe database operations.
""")

# Tabs for different views
tab_chat, tab_data = st.tabs(["💬 Chat", "📊 Database Viewer"])

with tab_chat:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask about your data (e.g., 'Show me all tables', 'How many users are there?')..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 Thinking...")
            
            try:
                # Call agent
                response = langgraph_agent.run_agent(prompt, st.session_state.thread_id)
                
                # Display response
                message_placeholder.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                message_placeholder.error(f"Error: {str(e)}")

with tab_data:
    st.subheader("Quick Data Explorer")
    
    # Refresh button
    if st.button("Refresh Tables"):
        st.rerun()
        
    try:
        tables = db_tools.list_tables()
        if not tables:
            st.info("No tables found in the database.")
        else:
            selected_table = st.selectbox("Select Table", tables)
            
            if selected_table:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Structure for `{selected_table}`**")
                    structure = db_tools.describe_table(selected_table)
                    st.dataframe(pd.DataFrame(structure), use_container_width=True)
                
                with col2:
                    st.markdown(f"**Data Preview for `{selected_table}`**")
                    # Limit preview to 100 rows
                    data = db_tools.execute_query(f"SELECT * FROM {selected_table} LIMIT 100")
                    if data:
                        st.dataframe(pd.DataFrame(data), use_container_width=True)
                    else:
                        st.info("Table is empty.")
                        
    except Exception as e:
        st.error(f"Error fetching database info: {str(e)}")

# Footer
st.markdown("---")
st.caption("Built with Streamlit, LangGraph, Ollama, and MCP")

# EXPLANATION
# Purpose: Streamlit user interface for the MCP PostgreSQL Agent
# Main functions: Chat interface for natural language queries, Database Viewer for manual exploration
# Notable vars: st.session_state.messages -> stores chat history, st.session_state.thread_id -> manages conversation context
