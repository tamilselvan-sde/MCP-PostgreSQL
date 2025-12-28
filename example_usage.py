#################################
#         example_usage.py
#################################

import langgraph_agent
import db_tools
print("----------------- langgraph_agent import completed or connected, ---------")
print("----------------- db_tools import completed or connected, ---------")

print("#===============[ start_of_main_process ]==========")

print("="*40)
# Example 1: Direct Database Access
print("="*40)

print("\nExample 1: Direct Database Operations")
print("-" * 40)

# List tables
print("\n1. Listing all tables:")
tables = db_tools.list_tables()
for table in tables:
    print(f"   - {table}")

# Create example table if needed
print("\n2. Ensuring example table exists:")
create_query = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    age INTEGER
)
"""
db_tools.execute_query(create_query)
print("   ✓ Table 'users' ready")

# Insert sample data
print("\n3. Inserting sample users:")
sample_users = [
    {"username": "alice", "email": "alice@example.com", "age": 28},
    {"username": "bob", "email": "bob@example.com", "age": 35}
]
for user in sample_users:
    user_id = db_tools.insert_record("users", user)
    print(f"   ✓ Inserted user '{user['username']}' with ID {user_id}")

print("="*40)
# Example 2: Agent-Based Queries
print("="*40)

print("\nExample 2: Using LangGraph Agent with Ollama")
print("-" * 40)

# Simple conversation
print("\n1. Simple greeting:")
response = langgraph_agent.run_agent(
    "Hello! What can you help me with?",
    thread_id="example_1"
)
print(f"   Agent: {response}")

# Request to use database tools
print("\n2. Asking agent to query database:")
response = langgraph_agent.run_agent(
    "Can you show me all the tables in the database?",
    thread_id="example_2"
)
print(f"   Agent: {response}")

# Complex database operation through agent
print("\n3. Complex query through agent:")
response = langgraph_agent.run_agent(
    "Can you query the users table and tell me the average age of all users?",
    thread_id="example_3"
)
print(f"   Agent: {response}")

print("="*40)
# Example 3: Conversation Memory
print("="*40)

print("\nExample 3: Demonstrating Conversation Memory")
print("-" * 40)

thread_id = "memory_demo"

print("\n1. First message (setting context):")
response = langgraph_agent.run_agent(
    "Please remember that my name is Sarah and I work at TechCorp.",
    thread_id=thread_id
)
print(f"   Agent: {response}")

print("\n2. Second message (testing memory):")
response = langgraph_agent.run_agent(
    "What is my name and where do I work?",
    thread_id=thread_id
)
print(f"   Agent: {response}")

print("="*40)
# Example 4: Data Analysis Request
print("="*40)

print("\nExample 4: Agent-Driven Data Analysis")
print("-" * 40)

response = langgraph_agent.run_agent(
    "Can you query the users table, count the total number of users, and find the oldest user?",
    thread_id="example_4"
)
print(f"   Agent: {response}")

print("="*40)
# Example 5: Multi-Step Workflow
print("="*40)

print("\nExample 5: Multi-Step Database Workflow")
print("-" * 40)

thread_id = "workflow_demo"

print("\n1. Request table description:")
response = langgraph_agent.run_agent(
    "First, describe the structure of the users table.",
    thread_id=thread_id
)
print(f"   Agent: {response}")

print("\n2. Request specific query:")
response = langgraph_agent.run_agent(
    "Now query all users where age is greater than 30.",
    thread_id=thread_id
)
print(f"   Agent: {response}")

print("#===============[ process completed ]==========")
print("\n✓ All examples completed successfully!")
print("\nKey Takeaways:")
print("  - Direct database access via db_tools module")
print("  - Natural language queries via LangGraph agent")
print("  - Automatic tool selection by Ollama LLM")
print("  - Persistent conversation memory across messages")
print("  - Complex multi-step workflows supported")

# EXPLANATION
# Purpose: Demonstrates complete end-to-end usage of MCP server with LangGraph and Ollama
# Main functions: Shows direct DB access, agent queries, memory persistence, multi-step workflows
# Notable vars: thread_id -> manages conversation sessions, sample_users -> demo data for examples
