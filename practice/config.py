GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL   = "gemini-2.5-flash"
"""
config.py — Updated with Aditi's real DB credentials
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Aditi's PostgreSQL DB — exact credentials from her db.py
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "agentic_sql_analyst"
DB_USER     = "postgres"
DB_PASSWORD = "postgres123"
 
# Safety
BLOCKED_SQL_KEYWORDS = ["DROP","DELETE","TRUNCATE","ALTER","UPDATE","INSERT","GRANT","REVOKE","CREATE"]
 
# Agent
MAX_CORRECTION_ATTEMPTS = 3
MAX_MEMORY_TURNS        = 10