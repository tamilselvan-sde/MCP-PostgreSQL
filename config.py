#################################
#         config.py
#################################

import os
from typing import Final
from dotenv import load_dotenv
print("----------------- os import completed or connected, ---------")
print("----------------- typing import completed or connected, ---------")
print("----------------- dotenv import completed or connected, ---------")

# Load environment variables
load_dotenv()
print("----------------- environment variables loaded, ---------")

print("="*40)
# PostgreSQL Configuration
print("="*40)

# Database connection parameters
DB_HOST: Final[str] = os.getenv("DB_HOST", "localhost")
DB_PORT: Final[int] = int(os.getenv("DB_PORT", "5432"))
DB_NAME: Final[str] = os.getenv("DB_NAME", "mcpdb")
DB_USER: Final[str] = os.getenv("DB_USER", "mcpuser")
DB_PASSWORD: Final[str] = os.getenv("DB_PASSWORD", "mcppassword")

# Connection string
DB_CONN_STRING: Final[str] = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("="*40)
# Ollama Configuration
print("="*40)

# Ollama endpoint and models
OLLAMA_ENDPOINT: Final[str] = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/")
OLLAMA_LLM_MODEL: Final[str] = os.getenv("OLLAMA_LLM_MODEL", "gpt-oss:120b-cloud")
OLLAMA_EMBED_MODEL: Final[str] = os.getenv("OLLAMA_EMBED_MODEL", "embeddinggemma:300m")

# LLM parameters
LLM_TEMPERATURE: Final[float] = float(os.getenv("LLM_TEMPERATURE", "0"))
LLM_MAX_TOKENS: Final[int] = int(os.getenv("LLM_MAX_TOKENS", "1000"))

print("="*40)
# validate_config
print("="*40)

def validate_config() -> bool:
    """Validate configuration parameters. Returns True if valid, False otherwise."""
    # Check database config
    if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
        print("ERROR: Missing database configuration")
        return False
    
    # Check Ollama config
    if not all([OLLAMA_ENDPOINT, OLLAMA_LLM_MODEL]):
        print("ERROR: Missing Ollama configuration")
        return False
    
    print("----------------- configuration validated successfully, ---------")
    return True

# EXPLANATION
# Purpose: Centralized configuration management for MCP server
# Main functions: validate_config -> validates all config params are present
# Notable vars: DB_CONN_STRING -> full PostgreSQL connection string, OLLAMA_ENDPOINT -> remote Ollama URL
