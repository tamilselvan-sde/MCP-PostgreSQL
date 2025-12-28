#################################
#         test_langgraph.py
#################################

import langgraph_agent
import config
print("----------------- langgraph_agent import completed or connected, ---------")
print("----------------- config import completed or connected, ---------")

print("#===============[ start_of_main_process ]==========")

print("="*40)
# Configuration Validation
print("="*40)

print("Validating configuration...")
if not config.validate_config():
    print("ERROR: Configuration validation failed")
    exit(1)

print("="*40)
# Test LLM Initialization
print("="*40)

print("\nTesting Ollama LLM initialization...")
try:
    llm = langgraph_agent.init_llm()
    print("----------------- LLM initialized successfully, ---------")
except Exception as e:
    print(f"ERROR: Failed to initialize LLM: {e}")
    exit(1)

print("="*40)
# Test Graph Building
print("="*40)

print("\nTesting LangGraph workflow construction...")
try:
    graph = langgraph_agent.build_graph()
    print("----------------- graph built successfully, ---------")
except Exception as e:
    print(f"ERROR: Failed to build graph: {e}")
    exit(1)

print("="*40)
# Test Simple Query
print("="*40)

print("\nTesting simple agent query...")
try:
    response = langgraph_agent.run_agent(
        "Hello! Can you introduce yourself?",
        thread_id="test_thread_1"
    )
    print(f"\nAgent response:\n{response}\n")
except Exception as e:
    print(f"ERROR: Agent query failed: {e}")

print("="*40)
# Test Database Tool Usage
print("="*40)

print("\nTesting agent with database tool request...")
try:
    response = langgraph_agent.run_agent(
        "Can you list all the tables in the database?",
        thread_id="test_thread_2"
    )
    print(f"\nAgent response:\n{response}\n")
except Exception as e:
    print(f"ERROR: Database tool query failed: {e}")

print("="*40)
# Test Table Description
print("="*40)

print("\nTesting agent with table description request...")
try:
    response = langgraph_agent.run_agent(
        "Can you describe the structure of the 'mcp_test' table if it exists?",
        thread_id="test_thread_3"
    )
    print(f"\nAgent response:\n{response}\n")
except Exception as e:
    print(f"ERROR: Table description query failed: {e}")

print("="*40)
# Test Conversation Memory
print("="*40)

print("\nTesting conversation memory...")
thread_id = "test_thread_memory"

try:
    print("First message:")
    response1 = langgraph_agent.run_agent(
        "My favorite number is 42",
        thread_id=thread_id
    )
    print(f"  Response: {response1}\n")
    
    print("Second message (testing memory):")
    response2 = langgraph_agent.run_agent(
        "What was my favorite number?",
        thread_id=thread_id
    )
    print(f"  Response: {response2}\n")
except Exception as e:
    print(f"ERROR: Memory test failed: {e}")

print("="*40)
# Test Complex Query
print("="*40)

print("\nTesting complex database query through agent...")
try:
    response = langgraph_agent.run_agent(
        "Can you query the mcp_test table and tell me how many records are in it?",
        thread_id="test_thread_4"
    )
    print(f"\nAgent response:\n{response}\n")
except Exception as e:
    print(f"ERROR: Complex query failed: {e}")

print("#===============[ process completed ]==========")
print("\n✓ All LangGraph agent tests completed!")

# EXPLANATION
# Purpose: Test script for LangGraph agent with Ollama integration
# Main functions: Tests LLM init, graph building, agent queries, tool usage, conversation memory
# Notable vars: thread_id -> conversation thread for memory testing, graph -> compiled LangGraph workflow
