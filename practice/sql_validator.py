#SQL Safety Validation
#(Read-only Guard)

#def validate_sql(sql):

#     blocked = [
#         "DELETE",
#         "DROP",
#         "UPDATE",
#         "INSERT",
#         "ALTER"
#     ]

#     sql_upper = sql.upper()

#     for word in blocked:

#         if word in sql_upper:
#             return False

#     return True
# if __name__ == "__main__":


    # print(validate_sql("SELECT * FROM sales"))
    # print(validate_sql("DELETE FROM sales"))
"""
sql_validator.py
Validates generated SQL before execution.
"""


def validate_sql(sql: str):

    if not sql or not sql.strip():
        return False, "Generated SQL is empty."

    sql = sql.strip()
    sql_upper = sql.upper()

    # ---------------------------------
    # Allow only SELECT or WITH queries
    # ---------------------------------
    if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
        return False, "Only SELECT queries are allowed."

    # ---------------------------------
    # Block dangerous statements
    # ---------------------------------
    blocked_keywords = [
        "DELETE",
        "DROP",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE"
    ]

    for keyword in blocked_keywords:
        if keyword in sql_upper:
            return False, f"Blocked SQL keyword detected: {keyword}"

    # ---------------------------------
    # Semicolon check
    # ---------------------------------
    if not sql.endswith(";"):
        return False, "SQL must end with ';'"

    # ---------------------------------
    # Parentheses check
    # ---------------------------------
    if sql.count("(") != sql.count(")"):
        return False, "Unbalanced parentheses."

    # ---------------------------------
    # Prevent incomplete CTE
    # ---------------------------------
    if "RANK()" in sql_upper or "DENSE_RANK()" in sql_upper:

        if "WITH" not in sql_upper:
            return False, "CTE is missing WITH clause."

    # ---------------------------------
    # Prevent accidental double semicolon
    # ---------------------------------
    if ";;" in sql:
        return False, "Invalid SQL syntax."

    return True, "SQL is valid."


if __name__ == "__main__":

    tests = [
        "SELECT * FROM orders;",
        "DELETE FROM orders;",
        "SELECT COUNT(*) FROM orders",
        "SELECT * FROM orders;;"
    ]

    for t in tests:
        print(validate_sql(t))