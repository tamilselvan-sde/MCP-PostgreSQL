#################################
#         langgraph_agent.py
#################################

from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
import config
import db_tools
print("----------------- typing imports completed or connected, ---------")
print("----------------- langchain imports completed or connected, ---------")
print("----------------- langgraph imports completed or connected, ---------")
print("----------------- config import completed or connected, ---------")
print("----------------- db_tools import completed or connected, ---------")

print("="*40)
# State
print("="*40)

class State(TypedDict):
    """State definition for LangGraph agent. Contains message history."""
    # Messages have the type "list". The add_messages function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list)
    messages: Annotated[list, add_messages]

print("="*40)
# Database Tools
print("="*40)

@tool
def db_query(query: str) -> str:
    """Execute SQL SELECT query and return results."""
    # Executes a database SELECT query and returns formatted results
    try:
        results = db_tools.execute_query(query)
        return f"Query returned {len(results)} rows: {results}"
    except Exception as e:
        return f"Error executing query: {str(e)}"

@tool
def db_list_tables() -> str:
    """List all tables in the database."""
    # Returns list of all tables in the database
    try:
        tables = db_tools.list_tables()
        return f"Available tables: {', '.join(tables)}"
    except Exception as e:
        return f"Error listing tables: {str(e)}"

@tool
def db_describe(table_name: str) -> str:
    """Describe the structure of a database table."""
    # Returns column information for a specified table
    try:
        columns = db_tools.describe_table(table_name)
        desc = [f"{c['column_name']} ({c['data_type']}, nullable: {c['is_nullable']})" 
                for c in columns]
        return f"Table '{table_name}' structure:\n" + "\n".join(desc)
    except Exception as e:
        return f"Error describing table: {str(e)}"

@tool
def db_insert(table: str, data: str) -> str:
    """Insert record into database table. Data should be JSON string."""
    # Inserts a new record into the specified table
    import json
    try:
        data_dict = json.loads(data)
        row_id = db_tools.insert_record(table, data_dict)
        return f"Record inserted successfully with ID: {row_id}"
    except Exception as e:
        return f"Error inserting record: {str(e)}"

@tool
def db_update(table: str, record_id: int, data: str) -> str:
    """Update record in database table. Data should be JSON string."""
    # Updates an existing record in the specified table
    import json
    try:
        data_dict = json.loads(data)
        success = db_tools.update_record(table, record_id, data_dict)
        return f"Record updated successfully: {success}"
    except Exception as e:
        return f"Error updating record: {str(e)}"

@tool
def db_delete(table: str, record_id: int) -> str:
    """Delete record from database table by ID."""
    # Deletes a record from the specified table
    try:
        success = db_tools.delete_record(table, record_id)
        return f"Record deleted successfully: {success}"
    except Exception as e:
        return f"Error deleting record: {str(e)}"

# All available tools
tools = [db_query, db_list_tables, db_describe, db_insert, db_update, db_delete]
print("----------------- database tools registered, ---------")

print("="*40)
# init_llm
print("="*40)

def init_llm():
    """Initialize Ollama LLM with tools. Returns LLM instance with bound tools."""
    # Creates and configures the Ollama LLM instance
    print("#===============[ init_llm ]==========")
    
    # Initialize chat model with remote Ollama endpoint
    llm = init_chat_model(
        f"ollama:{config.OLLAMA_LLM_MODEL}",
        base_url=config.OLLAMA_ENDPOINT,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS
    )
    print("----------------- Ollama LLM initialized, ---------")
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    print("----------------- tools bound to LLM, ---------")
    
    return llm_with_tools

print("="*40)
# chatbot
print("="*40)

def chatbot(state: State):
    """Chatbot node that processes messages and calls LLM. Returns updated state."""
    # Main chatbot node that processes user messages
    print("#===============[ chatbot node ]==========")
    llm = init_llm()
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

print("="*40)
# build_graph
print("="*40)

def build_graph():
    """Build LangGraph workflow. Returns compiled graph with memory."""
    # Constructs the LangGraph workflow with nodes and edges
    print("#===============[ build_graph ]==========")
    
    # Create graph
    graph_builder = StateGraph(State)
    
    # Add nodes
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools))
    print("----------------- graph nodes added, ---------")
    
    # Add edges
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition
    )
    graph_builder.add_edge("tools", "chatbot")
    print("----------------- graph edges added, ---------")
    
    # Add memory
    memory = MemorySaver()
    print("----------------- memory saver initialized, ---------")
    
    # Compile graph
    graph = graph_builder.compile(checkpointer=memory)
    print("----------------- graph compiled with memory, ---------")
    
    return graph

print("="*40)
# run_agent
print("="*40)

def run_agent(user_input: str, thread_id: str = "default") -> str:
    """Run agent with user input. Returns agent response."""
    # Executes the agent with a user message in a specific thread
    print("#===============[ run_agent ]==========")
    
    graph = build_graph()
    
    config_dict = {"configurable": {"thread_id": thread_id}}
    
    # Stream events
    events = graph.stream(
        {"messages": [("user", user_input)]},
        config_dict,
        stream_mode="values"
    )
    
    # Get final response
    response = ""
    for event in events:
        if "messages" in event and len(event["messages"]) > 0:
            last_msg = event["messages"][-1]
            if hasattr(last_msg, "content"):
                response = last_msg.content
    
    print(f"----------------- agent response generated, ---------")
    return response

print("="*40)
# interactive_chat
print("="*40)

def interactive_chat():
    """Interactive CLI chat interface. Provides user input options and commands."""
    # Interactive chat loop with command support
    print("#===============[ interactive_chat ]==========")
    print("\n" + "="*60)
    print("  🤖 MCP PostgreSQL Agent - Interactive Chat")
    print("="*60)
    print("\nAvailable Commands:")
    print("  /help      - Show this help message")
    print("  /thread ID - Switch to a different conversation thread")
    print("  /clear     - Clear current thread history")
    print("  /tables    - Quick list of database tables")
    print("  /exit      - Exit the chat")
    print("="*60 + "\n")
    
    thread_id = "default"
    print(f"Current thread: {thread_id}")
    print("Type your message or a command...\n")
    
    while True:
        try:
            # Get user input
            user_msg = input("You: ").strip()
            
            if not user_msg:
                continue
            
            # Handle commands
            if user_msg.startswith("/"):
                cmd = user_msg.lower().split()[0]
                
                if cmd == "/exit":
                    print("\n👋 Goodbye!")
                    print("#===============[ process completed ]==========")
                    break
                
                elif cmd == "/help":
                    print("\nAvailable Commands:")
                    print("  /help      - Show this help message")
                    print("  /thread ID - Switch to a different conversation thread")
                    print("  /clear     - Clear current thread history (not implemented)")
                    print("  /tables    - Quick list of database tables")
                    print("  /exit      - Exit the chat\n")
                    continue
                
                elif cmd == "/thread":
                    try:
                        new_thread = user_msg.split()[1]
                        thread_id = new_thread
                        print(f"✓ Switched to thread: {thread_id}\n")
                    except IndexError:
                        print("Usage: /thread <thread_id>\n")
                    continue
                
                elif cmd == "/clear":
                    print("⚠️  Clear history not fully implemented (memory persists in MemorySaver)")
                    print("   Switch to a new thread with: /thread <new_id>\n")
                    continue
                
                elif cmd == "/tables":
                    try:
                        tables = db_tools.list_tables()
                        print(f"\n📊 Tables: {', '.join(tables)}\n")
                    except Exception as e:
                        print(f"❌ Error: {e}\n")
                    continue
                
                else:
                    print(f"❌ Unknown command: {cmd}")
                    print("   Type /help for available commands\n")
                    continue
            
            # Send message to agent
            print("\n🤔 Agent thinking...")
            response = run_agent(user_msg, thread_id)
            print(f"\n🤖 Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            print("#===============[ process completed ]==========")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    print("#===============[ start_of_main_process ]==========")
    
    # Validate configuration
    if not config.validate_config():
        print("ERROR: Configuration validation failed")
        exit(1)
    
    # Test database connection
    if not db_tools.test_connection():
        print("ERROR: Database connection test failed")
        exit(1)
    
    # Start interactive chat
    interactive_chat()

# EXPLANATION
# Purpose: LangGraph agent with Ollama LLM and PostgreSQL tool integration
# Main functions: init_llm -> initializes Ollama with remote endpoint, build_graph -> creates workflow,
#                 chatbot -> main LLM node, run_agent -> executes agent with user input,
#                 interactive_chat -> CLI interface for interactive conversations
# Notable vars: tools -> list of database operation tools, State -> TypedDict with message history
