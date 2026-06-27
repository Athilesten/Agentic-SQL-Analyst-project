"""
sql_generator.py
----------------
Converts Natural Language to SQL using Google Gemini.
Author: Harshit | Project: Agentic SQL
"""

# #import os
# import re
# from pathlib import Path

# from dotenv import load_dotenv
# from google import genai

# from practice.prompt_template import build_sql_prompt


# load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# BLOCKED_SQL_KEYWORDS = [
#     "DROP", "DELETE", "TRUNCATE",
#     "ALTER", "UPDATE", "INSERT",
#     "CREATE", "REPLACE", "MERGE",
#     "GRANT", "REVOKE"
# ]


# class SQLGenerator:
#     def __init__(self):
#         if not GEMINI_API_KEY:
#             raise ValueError("GEMINI_API_KEY not found in .env file")

#         self.model_name = GEMINI_MODEL
#         self.client = genai.Client(api_key=GEMINI_API_KEY)

#     def generate_sql(
#         self,
#         user_question: str,
#         conversation_history: str = "",
#         use_live_db: bool = False
#     ) -> str:
#         if not user_question or not user_question.strip():
#             raise ValueError("Question cannot be empty")

#         prompt = build_sql_prompt(
#             user_question,
#             conversation_history,
#             use_live_db
#         )

#         response_text = self._call_gemini(prompt)
#         sql = self._clean(response_text)
#         self._validate(sql)

#         return sql

#     def call_gemini_raw(self, prompt: str) -> str:
#         """
#         Used by correction_loop.py.
#         Sends raw prompt directly to Gemini.
#         """
#         return self._call_gemini(prompt)

#     def _call_gemini(self, prompt: str) -> str:
#         try:
#             response = self.client.models.generate_content(
#                 model=self.model_name,
#                 contents=prompt
#             )

#             if not response or not getattr(response, "text", None):
#                 raise ValueError("Gemini returned empty response")

#             return response.text.strip()

#         except Exception as e:
#             error_text = str(e).lower()

#             if (
#                 "getaddrinfo failed" in error_text
#                 or "name resolution" in error_text
#                 or "dns" in error_text
#                 or "connection" in error_text
#             ):
#                 raise ConnectionError(
#                     "Network/DNS error: Gemini API is not reachable. "
#                     "Please check internet, DNS, VPN/proxy, and API key."
#                 )

#             raise

#     @staticmethod
#     def _clean(text: str) -> str:
#         if not text:
#             raise ValueError("Gemini returned empty response")

#         text = text.strip()

#         # Remove markdown fences if Gemini returns ```sql ... ```
#         text = re.sub(r"```sql", "", text, flags=re.IGNORECASE)
#         text = text.replace("```", "").strip()

#         # Try to extract SQL starting from SELECT or WITH
#         match = re.search(
#             r"\b(WITH|SELECT)\b[\s\S]*?;",
#             text,
#             flags=re.IGNORECASE
#         )

#         if match:
#             sql = match.group(0).strip()
#         else:
#             # Fallback: collect from first SELECT/WITH line
#             lines = text.splitlines()
#             collecting = False
#             parts = []

#             for line in lines:
#                 clean_line = line.strip()
#                 upper_line = clean_line.upper()

#                 if upper_line.startswith("SELECT") or upper_line.startswith("WITH"):
#                     collecting = True

#                 if collecting:
#                     parts.append(clean_line)

#             sql = " ".join(parts) if parts else text.strip()

#         sql = re.sub(r"\s+", " ", sql).strip()

#         if sql and not sql.endswith(";"):
#             sql += ";"

#         return sql

#     @staticmethod
#     def _validate(sql: str):
#         if not sql:
#             raise ValueError("Generated SQL is empty")

#         upper = sql.upper().strip()

#         if not (upper.startswith("SELECT") or upper.startswith("WITH")):
#             raise ValueError("Only SELECT or WITH SELECT queries are allowed")

#         for keyword in BLOCKED_SQL_KEYWORDS:
#             if re.search(r"\b" + keyword + r"\b", upper):
#                 raise ValueError(
#                     f"Blocked keyword '{keyword}' in generated SQL. "
#                     "Only safe SELECT queries are allowed."
#                 )

#         if sql.count("(") != sql.count(")"):
#             raise ValueError("Unbalanced parentheses in generated SQL")

#         if sql.count(";") > 1:
#             raise ValueError("Multiple SQL statements are not allowed")


# def generate_sql(question):
#     """
#     Wrapper function for older modules.
#     """
#     generator = SQLGenerator()
#     return generator.generate_sql(question)


# if __name__ == "__main__":
#     gen = SQLGenerator()

#     questions = [
#         "Show total revenue",
#         "Show top 5 products by revenue",
#         "Show revenue by category",
#         "How many total orders",
#         "Show top 5 customers by spending",
#         "Show all products whose revenue is greater than the average revenue of all products"
#     ]

#     for q in questions:
#         print(f"\nQ: {q}")
#         try:
#             print(f"SQL: {gen.generate_sql(q)}")
#         except Exception as e:
#             print(f"ERROR: {e}")
#         print("-" * 55)

"""
sql_generator.py
----------------
Generates safe PostgreSQL SELECT queries from natural-language questions using
Google Gemini.
"""

import os
import re
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google import genai

from practice.prompt_template import build_sql_prompt


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

BLOCKED_SQL_KEYWORDS = {
    "DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT",
    "CREATE", "REPLACE", "MERGE", "GRANT", "REVOKE", "CALL", "EXEC"
}


class SQLGenerator:
    """Generate and validate read-only SQL queries."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or GEMINI_MODEL

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")

        self.client = genai.Client(api_key=self.api_key)

    def generate_sql(
        self,
        user_question: str,
        conversation_history: str = "",
        use_live_db: bool = False
    ) -> str:
        """Generate one safe PostgreSQL SELECT query for a business question."""
        question = self._normalize_question(user_question)

        prompt = build_sql_prompt(
            question,
            conversation_history or "",
            use_live_db
        )

        response_text = self._call_gemini(prompt)
        sql = self.clean_sql(response_text)
        self.validate_sql(sql)

        return sql

    def call_gemini_raw(self, prompt: str) -> str:
        """Call Gemini directly. Used by SQL correction flow."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        return self._call_gemini(prompt)

    def _call_gemini(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            response_text = getattr(response, "text", None)

            if not response_text or not response_text.strip():
                raise ValueError("Gemini returned an empty response.")

            return response_text.strip()

        except Exception as exc:
            if self._is_network_error(exc):
                raise ConnectionError(
                    "Gemini API is not reachable. Check internet access, DNS, "
                    "VPN/proxy settings, and the configured API key."
                ) from exc

            raise RuntimeError(f"Gemini SQL generation failed: {exc}") from exc

    @staticmethod
    def clean_sql(response_text: str) -> str:
        """Extract a single SQL statement from a model response."""
        if not response_text or not response_text.strip():
            raise ValueError("Model returned an empty SQL response.")

        text = response_text.strip()

        text = re.sub(r"```(?:sql)?", "", text, flags=re.IGNORECASE).strip()
        text = text.replace("```", "").strip()

        statement = SQLGenerator._extract_select_statement(text)
        statement = re.sub(r"\s+", " ", statement).strip()

        if not statement.endswith(";"):
            statement += ";"

        return statement

    @staticmethod
    def validate_sql(sql: str) -> bool:
        """Validate that SQL is read-only and contains exactly one statement."""
        if not sql or not sql.strip():
            raise ValueError("Generated SQL is empty.")

        normalized = re.sub(r"\s+", " ", sql).strip()
        upper_sql = normalized.upper()

        if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
            raise ValueError("Only SELECT queries or WITH ... SELECT queries are allowed.")

        if normalized.count(";") > 1:
            raise ValueError("Multiple SQL statements are not allowed.")

        for keyword in BLOCKED_SQL_KEYWORDS:
            if re.search(rf"\b{keyword}\b", upper_sql):
                raise ValueError(
                    f"Blocked keyword '{keyword}' found. Only read-only SELECT queries are allowed."
                )

        if normalized.count("(") != normalized.count(")"):
            raise ValueError("Generated SQL has unbalanced parentheses.")

        return True

    @staticmethod
    def _extract_select_statement(text: str) -> str:
        semicolon_match = re.search(
            r"\b(WITH|SELECT)\b[\s\S]*?;",
            text,
            flags=re.IGNORECASE
        )

        if semicolon_match:
            return semicolon_match.group(0).strip()

        start_match = re.search(r"\b(WITH|SELECT)\b", text, flags=re.IGNORECASE)

        if not start_match:
            raise ValueError("No SELECT query found in model response.")

        return text[start_match.start():].strip()

    @staticmethod
    def _normalize_question(question: str) -> str:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        return re.sub(r"\s+", " ", question).strip()

    @staticmethod
    def _is_network_error(error: Exception) -> bool:
        error_text = str(error).lower()

        network_terms = (
            "getaddrinfo failed",
            "name resolution",
            "dns",
            "connection",
            "connection reset",
            "connection refused",
            "timed out",
            "timeout",
            "network",
        )

        return any(term in error_text for term in network_terms)


def generate_sql(question: str) -> str:
    """Backward-compatible wrapper for older modules."""
    generator = SQLGenerator()
    return generator.generate_sql(question)


if __name__ == "__main__":
    generator = SQLGenerator()

    sample_questions = [
        "Show total revenue",
        "Show top 5 products by revenue",
        "Show revenue by category",
        "How many total orders?",
        "Show top 5 customers by spending",
        "Show all products whose revenue is greater than the average product revenue",
    ]

    for sample_question in sample_questions:
        print(f"\nQuestion: {sample_question}")

        try:
            print(f"SQL: {generator.generate_sql(sample_question)}")
        except Exception as exc:
            print(f"Error: {exc}")

        print("-" * 60)