#################################
#         db_tools.py
#################################

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import config
print("----------------- psycopg2 import completed or connected, ---------")
print("----------------- typing import completed or connected, ---------")
print("----------------- contextlib import completed or connected, ---------")
print("----------------- config import completed or connected, ---------")

print("="*40)
# get_db_connection
print("="*40)

@contextmanager
def get_db_connection():
    """Get database connection context manager. Yields connection with RealDictCursor."""
    # Context manager for safe database connections with automatic cleanup
    conn = None
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        print("----------------- database connection established, ---------")
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Database connection failed: {e}")
        raise
    finally:
        if conn:
            conn.close()
            print("----------------- database connection closed, ---------")

print("="*40)
# execute_query
print("="*40)

def execute_query(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """Execute SELECT query and return results as list of dicts. Params are optional query parameters."""
    # Executes a SELECT query with optional parameters, returns results
    print("#===============[ execute_query ]==========")
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            # Check if query returns results (SELECT, RETURNING, etc.)
            if cur.description:
                results = [dict(row) for row in cur.fetchall()]
                print(f"----------------- query executed, returned {len(results)} rows, ---------")
                return results
            else:
                # DDL or DML without RETURNING clause
                print(f"----------------- query executed successfully (no results), ---------")
                return []

print("="*40)
# insert_record
print("="*40)

def insert_record(table: str, data: Dict[str, Any]) -> int:
    """Insert record into table. Returns inserted row ID."""
    # Inserts a new record into specified table with provided data
    print("#===============[ insert_record ]==========")
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(data.values()))
            row_id = cur.fetchone()[0]
            print(f"----------------- record inserted with ID {row_id}, ---------")
            return row_id

print("="*40)
# update_record
print("="*40)

def update_record(table: str, record_id: int, data: Dict[str, Any]) -> bool:
    """Update record in table by ID. Returns True if successful."""
    # Updates an existing record with new data based on ID
    print("#===============[ update_record ]==========")
    set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE id = %s"
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(data.values()) + (record_id,))
            success = cur.rowcount > 0
            print(f"----------------- record updated: {success}, ---------")
            return success

print("="*40)
# delete_record
print("="*40)

def delete_record(table: str, record_id: int) -> bool:
    """Delete record from table by ID. Returns True if successful."""
    # Deletes a record from table based on ID
    print("#===============[ delete_record ]==========")
    query = f"DELETE FROM {table} WHERE id = %s"
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (record_id,))
            success = cur.rowcount > 0
            print(f"----------------- record deleted: {success}, ---------")
            return success

print("="*40)
# list_tables
print("="*40)

def list_tables() -> List[str]:
    """List all tables in database. Returns list of table names."""
    # Retrieves all table names from the current database schema
    print("#===============[ list_tables ]==========")
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """
    results = execute_query(query)
    tables = [row['table_name'] for row in results]
    print(f"----------------- found {len(tables)} tables, ---------")
    return tables

print("="*40)
# describe_table
print("="*40)

def describe_table(table: str) -> List[Dict[str, str]]:
    """Describe table structure. Returns list of column info dicts with name, type, nullable."""
    # Gets detailed column information for a specified table
    print("#===============[ describe_table ]==========")
    query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """
    results = execute_query(query, (table,))
    print(f"----------------- table '{table}' has {len(results)} columns, ---------")
    return results

print("="*40)
# test_connection
print("="*40)

def test_connection() -> bool:
    """Test database connection. Returns True if connection successful."""
    # Tests if database is reachable and connection can be established
    print("#===============[ test_connection ]==========")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                success = result[0] == 1
                print(f"----------------- connection test: {success}, ---------")
                return success
    except Exception as e:
        print(f"ERROR: Connection test failed: {e}")
        return False

# EXPLANATION
# Purpose: PostgreSQL database operations for MCP server
# Main functions: execute_query -> runs SELECT queries, insert_record -> adds new rows, 
#                 update_record -> modifies existing rows, delete_record -> removes rows,
#                 list_tables -> gets all table names, describe_table -> shows table structure
# Notable vars: get_db_connection -> context manager for safe DB access with auto-cleanup
