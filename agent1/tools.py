"""
tools.py
Execute SQL queries on PostgreSQL.
"""

import psycopg2
import pandas as pd


# PostgreSQL Configuration
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "agentic_sql_analyst",
    "user": "postgres",
    "password": "postgres123"
}


def execute_sql(sql):

    print("Executing SQL:")
    print(sql)

    conn = None
    cursor = None

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Execute SQL
        cursor.execute(sql)

        # Fetch all rows
        rows = cursor.fetchall()

        # Fetch column names
        columns = [desc[0] for desc in cursor.description]

        print(f"Result: {len(rows)} rows returned")

        # Return BOTH columns and rows
        return columns, rows

    except Exception as e:
        print(f"DB Error: {e}")
        raise

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


if __name__ == "__main__":

    columns, rows = execute_sql(
        "SELECT COUNT(*) AS total_orders FROM orders;"
    )

    print("Columns:", columns)
    print("Rows:", rows)