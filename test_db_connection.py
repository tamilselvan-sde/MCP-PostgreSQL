#################################
#         test_db_connection.py
#################################

import db_tools
import config
print("----------------- db_tools import completed or connected, ---------")
print("----------------- config import completed or connected, ---------")

print("#===============[ start_of_main_process ]==========")

print("="*40)
# Configuration Validation
print("="*40)

print("Testing PostgreSQL connection...")
if not config.validate_config():
    print("ERROR: Configuration validation failed")
    exit(1)

print("="*40)
# Connection Test
print("="*40)

print("Testing database connection...")
if not db_tools.test_connection():
    print("ERROR: Connection test failed")
    exit(1)

print("="*40)
# List Tables
print("="*40)

print("\nListing existing tables...")
tables = db_tools.list_tables()
print(f"Found {len(tables)} tables:")
for table in tables:
    print(f"  - {table}")

print("="*40)
# Create Test Table
print("="*40)

print("\nCreating test table 'mcp_test'...")
create_query = """
CREATE TABLE IF NOT EXISTS mcp_test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    value INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
try:
    db_tools.execute_query(create_query)
    print("----------------- test table created, ---------")
except Exception as e:
    print(f"Table may already exist or error occurred: {e}")

print("="*40)
# Describe Table
print("="*40)

print("\nDescribing 'mcp_test' table structure...")
columns = db_tools.describe_table("mcp_test")
for col in columns:
    print(f"  {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")

print("="*40)
# Insert Test Data
print("="*40)

print("\nInserting test records...")
test_data = [
    {"name": "test_record_1", "value": 100},
    {"name": "test_record_2", "value": 200},
    {"name": "test_record_3", "value": 300}
]

inserted_ids = []
for data in test_data:
    row_id = db_tools.insert_record("mcp_test", data)
    inserted_ids.append(row_id)
    print(f"  Inserted record with ID: {row_id}")

print("="*40)
# Query Test Data
print("="*40)

print("\nQuerying all records from mcp_test...")
results = db_tools.execute_query("SELECT * FROM mcp_test ORDER BY id")
print(f"Found {len(results)} records:")
for row in results:
    print(f"  ID: {row['id']}, Name: {row['name']}, Value: {row['value']}")

print("="*40)
# Update Test
print("="*40)

if inserted_ids:
    test_id = inserted_ids[0]
    print(f"\nUpdating record with ID {test_id}...")
    success = db_tools.update_record("mcp_test", test_id, {"value": 999})
    print(f"Update success: {success}")
    
    # Verify update
    updated = db_tools.execute_query(f"SELECT * FROM mcp_test WHERE id = {test_id}")
    if updated:
        print(f"  Updated value: {updated[0]['value']}")

print("="*40)
# Delete Test
print("="*40)

if len(inserted_ids) > 1:
    test_id = inserted_ids[-1]
    print(f"\nDeleting record with ID {test_id}...")
    success = db_tools.delete_record("mcp_test", test_id)
    print(f"Delete success: {success}")

print("="*40)
# Final Count
print("="*40)

print("\nFinal record count...")
final_results = db_tools.execute_query("SELECT COUNT(*) as count FROM mcp_test")
print(f"Total records in mcp_test: {final_results[0]['count']}")

print("#===============[ process completed ]==========")
print("\n✓ All database operations completed successfully!")

# EXPLANATION
# Purpose: Test script for PostgreSQL database connection and operations
# Main functions: Tests connection, creates table, inserts/updates/deletes records, queries data
# Notable vars: test_data -> sample records for testing, inserted_ids -> tracks created record IDs
