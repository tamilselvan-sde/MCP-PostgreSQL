#################################
#         mcp_postgres_server.py
#################################

import asyncio
import json
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import config
import db_tools
import langgraph_agent
print("----------------- asyncio import completed or connected, ---------")
print("----------------- json import completed or connected, ---------")
print("----------------- typing import completed or connected, ---------")
print("----------------- mcp imports completed or connected, ---------")
print("----------------- config import completed or connected, ---------")
print("----------------- db_tools import completed or connected, ---------")
print("----------------- langgraph_agent import completed or connected, ---------")

print("="*40)
# MCP Server Initialization
print("="*40)

# Create MCP server instance
server = Server("postgres-mcp-server")
print("----------------- MCP server instance created, ---------")

print("="*40)
# list_tools_handler
print("="*40)

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools. Returns list of Tool objects."""
    # Returns all available database and agent tools
    print("#===============[ list_tools ]==========")
    
    tools_list = [
        Tool(
            name="db_query",
            description="Execute SQL SELECT query and return results",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL SELECT query to execute"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="db_list_tables",
            description="List all tables in the PostgreSQL database",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="db_describe",
            description="Describe the structure of a database table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Name of the table to describe"}
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="db_insert",
            description="Insert a new record into a database table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {"type": "string", "description": "Table name"},
                    "data": {"type": "string", "description": "JSON string of data to insert"}
                },
                "required": ["table", "data"]
            }
        ),
        Tool(
            name="db_update",
            description="Update an existing record in a database table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {"type": "string", "description": "Table name"},
                    "record_id": {"type": "integer", "description": "ID of record to update"},
                    "data": {"type": "string", "description": "JSON string of data to update"}
                },
                "required": ["table", "record_id", "data"]
            }
        ),
        Tool(
            name="db_delete",
            description="Delete a record from a database table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {"type": "string", "description": "Table name"},
                    "record_id": {"type": "integer", "description": "ID of record to delete"}
                },
                "required": ["table", "record_id"]
            }
        ),
        Tool(
            name="agent_query",
            description="Ask the LangGraph agent a question (uses Ollama LLM with database access)",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Question to ask the agent"},
                    "thread_id": {"type": "string", "description": "Conversation thread ID (optional)", "default": "default"}
                },
                "required": ["question"]
            }
        )
    ]
    
    print(f"----------------- listed {len(tools_list)} tools, ---------")
    return tools_list

print("="*40)
# call_tool_handler
print("="*40)

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool execution requests. Returns list of TextContent with results."""
    # Routes tool calls to appropriate handlers
    print(f"#===============[ call_tool: {name} ]==========")
    
    try:
        result = ""
        
        if name == "db_query":
            query = arguments.get("query", "")
            results = db_tools.execute_query(query)
            result = json.dumps(results, indent=2)
            
        elif name == "db_list_tables":
            tables = db_tools.list_tables()
            result = json.dumps({"tables": tables}, indent=2)
            
        elif name == "db_describe":
            table_name = arguments.get("table_name", "")
            columns = db_tools.describe_table(table_name)
            result = json.dumps(columns, indent=2)
            
        elif name == "db_insert":
            table = arguments.get("table", "")
            data = arguments.get("data", "{}")
            data_dict = json.loads(data)
            row_id = db_tools.insert_record(table, data_dict)
            result = json.dumps({"success": True, "id": row_id}, indent=2)
            
        elif name == "db_update":
            table = arguments.get("table", "")
            record_id = arguments.get("record_id", 0)
            data = arguments.get("data", "{}")
            data_dict = json.loads(data)
            success = db_tools.update_record(table, record_id, data_dict)
            result = json.dumps({"success": success}, indent=2)
            
        elif name == "db_delete":
            table = arguments.get("table", "")
            record_id = arguments.get("record_id", 0)
            success = db_tools.delete_record(table, record_id)
            result = json.dumps({"success": success}, indent=2)
            
        elif name == "agent_query":
            question = arguments.get("question", "")
            thread_id = arguments.get("thread_id", "default")
            response = langgraph_agent.run_agent(question, thread_id)
            result = response
            
        else:
            result = json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
        
        print(f"----------------- tool '{name}' executed successfully, ---------")
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        error_msg = f"Error executing tool '{name}': {str(e)}"
        print(f"ERROR: {error_msg}")
        return [TextContent(type="text", text=json.dumps({"error": error_msg}, indent=2))]

print("="*40)
# main
print("="*40)

async def main():
    """Main entry point for MCP server. Runs server with stdio transport."""
    # Starts the MCP server and handles communication
    print("#===============[ start_of_main_process ]==========")
    
    # Validate configuration
    if not config.validate_config():
        print("ERROR: Configuration validation failed")
        return
    
    # Test database connection
    if not db_tools.test_connection():
        print("ERROR: Database connection test failed")
        return
    
    print("----------------- MCP server starting with stdio transport, ---------")
    
    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
    
    print("#===============[ process completed ]==========")

if __name__ == "__main__":
    print("#===============[ start_of_main_process ]==========")
    asyncio.run(main())

# EXPLANATION
# Purpose: MCP server implementing Model Context Protocol for PostgreSQL access with LangGraph agent
# Main functions: list_tools -> returns available MCP tools, call_tool -> executes tool requests,
#                 main -> starts server with stdio transport
# Notable vars: server -> MCP Server instance, tools_list -> available database and agent operations
