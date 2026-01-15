# =========================
# config.py
# Centralized configuration file for the project
# =========================



# ========================================================================================
# comments are added for clarity
# ========================================================================================

"""
==============================================================================
CONFIGURATION MODULE - Supports both .env and Streamlit secrets
==============================================================================
Priority:
1. Streamlit secrets (st.secrets) - when running in Streamlit
2. Environment variables (.env file)
3. Default values
==============================================================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import Streamlit secrets (only available when running in Streamlit)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def get_secret(key: str, default=None):
    """
    Get configuration value with priority:
    1. Streamlit secrets (if available)
    2. Environment variables
    3. Default value
    """
    # Try Streamlit secrets first
    if HAS_STREAMLIT:
        try:
            return st.secrets.get(key, os.getenv(key, default))
        except Exception:
            # Secrets not configured or not in Streamlit context
            pass
    
    # Fall back to environment variables
    return os.getenv(key, default)


# =========================
# PROJECT PATHS
# =========================

BANK_NAME = get_secret("BANK_NAME", "Sample Bank")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

# =========================
# LLM CONFIGURATION
# =========================

GROQ_API_KEY = get_secret("GROQ_API_KEY")
GROQ_MODEL = get_secret("GROQ_MODEL", "llama-3.3-70b-versatile")

# Validate API key exists
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found! Add it to:\n"
        "  - .env file (local development), OR\n"
        "  - .streamlit/secrets.toml (Streamlit Cloud)"
    )

# =========================
# LANGSMITH OBSERVABILITY
# =========================

LANGCHAIN_TRACING_V2 = get_secret("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_API_KEY = get_secret("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = get_secret("LANGCHAIN_PROJECT", "agentic-ai-poc-2")
LANGCHAIN_ENDPOINT = get_secret("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

# Set LangSmith environment variables for tracing
if LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
    print(f"✅ LangSmith tracing enabled: {LANGCHAIN_PROJECT}")
else:
    print("⚠️ LangSmith tracing disabled (set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY)")

# =========================
# VECTOR STORE
# =========================

CHROMA_PERSIST_DIR = get_secret("CHROMA_PERSIST_DIR", "./vectorstore/chroma_db")
EMBEDDING_MODEL = get_secret("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")

# =========================
# AGENT SETTINGS
# =========================

BANKING_AGENT_TEMPERATURE = float(get_secret("BANKING_AGENT_TEMPERATURE", "0.1"))
MARKETING_AGENT_TEMPERATURE = float(get_secret("MARKETING_AGENT_TEMPERATURE", "0.7"))
MAX_ITERATIONS = int(get_secret("MAX_ITERATIONS", "5"))
ENABLE_MEMORY = get_secret("ENABLE_MEMORY", "true").lower() == "true"

# =========================
# API SERVER
# =========================

API_HOST = get_secret("API_HOST", "0.0.0.0")
API_PORT = int(get_secret("API_PORT", "8000"))
ENVIRONMENT = get_secret("ENVIRONMENT", "development")

# =========================
# COLLECTION NAMES
# =========================

BANKING_COLLECTION = "banking_products"
MARKETING_COLLECTION = "marketing_campaigns"







""" This is the original version without Streamlit secrets support and is commented out for reference."""

# import os  # Imports the built-in os module to interact with environment variables and the operating system
# from pathlib import Path  # Imports Path to handle filesystem paths in an OS-independent way
# from dotenv import load_dotenv  # Imports load_dotenv to load variables from a .env file into the environment

# # Load environment variables from the .env file into the current process environment
# load_dotenv()

# # =========================
# # PROJECT PATHS
# # =========================


# BANK_NAME = os.getenv("BANK_NAME", "Sample Bank")
# # Reads the BANK_NAME environment variable.

# BASE_DIR = Path(__file__).resolve().parent  
# # __file__ gives the current file path
# # resolve() converts it to an absolute path (resolving symlinks if any)
# # parent extracts the directory containing this file
# # BASE_DIR now represents the root directory of this project

# DATA_DIR = BASE_DIR / "data"  
# # Constructs a path pointing to a "data" folder inside the project root
# # The "/" operator is overloaded by Path to safely join paths

# VECTORSTORE_DIR = BASE_DIR / "vectorstore"  
# # Constructs a path pointing to a "vectorstore" directory inside the project root

# # =========================
# # LLM CONFIGURATION
# # =========================

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")  
# # Reads the GROQ_API_KEY value from environment variables
# # Returns None if the variable is not defined

# GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  
# # Reads the GROQ_MODEL environment variable
# # Defaults to "llama-3.3-70b-versatile" if not provided

# # Validate API key exists
# if not GROQ_API_KEY:  
#     # Checks whether GROQ_API_KEY is missing or empty
#     raise ValueError("GROQ_API_KEY not found in environment variables")  
#     # Raises an explicit error to fail fast if the API key is not configured

# # =========================
# # LANGSMITH OBSERVABILITY
# # =========================

# LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
# LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
# LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "agentic-ai-poc-2")
# LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

# # Set LangSmith environment variables for tracing (NEW!)
# if LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY:
#     os.environ["LANGCHAIN_TRACING_V2"] = "true"
#     os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
#     os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
#     os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
#     print(f" LangSmith tracing enabled: {LANGCHAIN_PROJECT}")
# else:
#     print("⚠️ LangSmith tracing disabled (set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY)")

# # =========================
# # VECTOR STORE
# # =========================

# CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./vectorstore/chroma_db")  
# # Reads the directory where Chroma vector DB should persist data
# # Defaults to "./vectorstore/chroma_db" if not provided

# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5") 
# # Reads the embedding model name from environment variables
# # Defaults to a lightweight and commonly used sentence transformer model

# # =========================
# # AGENT SETTINGS
# # =========================

# BANKING_AGENT_TEMPERATURE = float(
#     os.getenv("BANKING_AGENT_TEMPERATURE", "0.1")
# )  
# # Reads temperature for the banking agent as a string
# # Converts it to float to control randomness (lower = more deterministic)

# MARKETING_AGENT_TEMPERATURE = float(
#     os.getenv("MARKETING_AGENT_TEMPERATURE", "0.7")
# )  
# # Reads temperature for the marketing agent
# # Higher value allows more creativity and variation in responses

# MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "5"))  
# # Reads the maximum number of agent reasoning iterations
# # Converts the value to integer for loop/control logic

# ENABLE_MEMORY = os.getenv("ENABLE_MEMORY", "true").lower() == "true"  
# # Reads ENABLE_MEMORY as a string
# # Converts it to lowercase
# # Compares it to "true" to produce a boolean value

# # =========================
# # API SERVER
# # =========================

# API_HOST = os.getenv("API_HOST", "0.0.0.0")  
# # Reads the API host address
# # Defaults to "0.0.0.0" to allow external access

# API_PORT = int(os.getenv("API_PORT", "8000"))  
# # Reads the API port number as a string
# # Converts it to an integer for server binding

# ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  
# # Reads the environment mode (development / staging / production)
# # Defaults to "development"

# # =========================
# # COLLECTION NAMES
# # =========================

# BANKING_COLLECTION = "banking_products"  
# # Defines the collection name used for banking-related vector data

# MARKETING_COLLECTION = "marketing_campaigns"  
# # Defines the collection name used for marketing-related vector data










# What you SHOULD do next (one command that solves everything)

# For your actual project:
# cd C:\Users\ag181\Documents\Eeshanya\..SEM_LONG_TCS\poc\second
# python -m venv .venv
# .venv\Scripts\activate
# python -m pip install chromadb sentence-transformers fastapi uvicorn


# Inside .venv:
# pip check will be CLEAN
# No warnings
# No conflicts
# Demo-safe for mentor