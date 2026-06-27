"""
prompt_template.py - Short prompt to stay within free tier limits
"""
from practice.schema_reader import get_schema
# #def build_sql_prompt(user_question: str,
#                      conversation_history: str = "",
#                      use_live_db: bool = False) -> str:
#     return f"""Convert to PostgreSQL SQL. Return ONLY the SQL query, nothing else.

# Tables: customers(customer_id,country,signup_date), products(product_id,product_name,category,price), orders(order_id,customer_id,order_date,status), order_items(order_id,product_id,quantity,price)

# Note: revenue = quantity * price

# Question: {user_question}
# SQL:"""
from practice.schema_reader import get_schema

def build_sql_prompt(user_question: str,
                     conversation_history: str = "",
                     use_live_db: bool = False) -> str:

    schema = get_schema()

    return f"""
You are an expert PostgreSQL SQL Generator.

Database Schema:
{schema}

Rules:
1. Return ONLY executable PostgreSQL SQL.
2. Do NOT explain anything.
3. Do NOT use Markdown.
4. Do NOT generate DELETE, DROP, UPDATE, INSERT, ALTER, CREATE or TRUNCATE.
5. Use ONLY the tables and columns given in the schema.
6. Always generate a complete SQL query.
7. Never generate incomplete CTEs.
8. If using WITH, write the complete WITH clause.
9. Use proper JOIN conditions.
10. Always end the SQL with a semicolon.
11. Revenue means quantity * price.
12. If the question asks for Top N, use ORDER BY with LIMIT.
13. If the question asks for second highest, prefer:
    ORDER BY ... DESC OFFSET 1 LIMIT 1
    instead of DENSE_RANK unless absolutely necessary.

Previous Conversation:
{conversation_history}

User Question:
{user_question}

SQL:
"""

# def build_correction_prompt(original_question, failed_sql, error_message, use_live_db=False):
#     return f"""Fix this PostgreSQL SQL. Return ONLY corrected SQL.

# Tables: customers(customer_id,country,signup_date), products(product_id,product_name,category,price), orders(order_id,customer_id,order_date,status), order_items(order_id,product_id,quantity,price)

# Question: {original_question}
# Failed SQL: {failed_sql}
# Error: {error_message}
# Fixed SQL:"""
def build_correction_prompt(original_question,
                            failed_sql,
                            error_message,
                            use_live_db=False):

    schema = get_schema()

    return f"""
You generated invalid PostgreSQL SQL.

Database Schema:
{schema}

Original Question:
{original_question}

Generated SQL:
{failed_sql}

Database Error:
{error_message}

Rules:
1. Rewrite the ENTIRE SQL query.
2. Return ONLY SQL.
3. Never repeat the same mistake.
4. Use only existing tables and columns.
5. Do not generate incomplete CTEs.
6. Ensure PostgreSQL syntax is valid.
7. End with semicolon.

Correct SQL:
"""

def build_insights_prompt(user_question, sql_query, query_results):
    return f"""Write a 2 sentence business insight.
Question: {user_question}
Results: {query_results}
Insight:"""