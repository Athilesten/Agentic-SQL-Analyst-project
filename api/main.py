"""
api/main.py
FastAPI Backend for Agentic SQL Data Analyst

This backend handles:
1. Login authentication
2. Dashboard metrics
3. Natural language query processing
4. PostgreSQL history storage
5. History fetching
6. History clearing
"""

import os
from decimal import Decimal
from datetime import date, datetime

import pandas as pd
import psycopg2
from psycopg2.extras import Json

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent1.agent_workflow import run_agent
from agent1.tools import execute_sql, DB_CONFIG


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()

APP_USERNAME = os.getenv("APP_USERNAME", "harshit")
APP_PASSWORD = os.getenv("APP_PASSWORD", "admin123")


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="Agentic SQL Data Analyst API",
    description="Backend API for Natural Language to SQL Data Analyst",
    version="1.0.0"
)


# =====================================================
# REQUEST MODELS
# =====================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class QueryRequest(BaseModel):
    username: str
    question: str


class HistoryRequest(BaseModel):
    username: str


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def make_json_safe(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, tuple):
        return [make_json_safe(item) for item in value]

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    if isinstance(value, dict):
        return {
            key: make_json_safe(val)
            for key, val in value.items()
        }

    return value


def sql_value(sql):
    try:
        columns, rows = execute_sql(sql)

        if rows:
            return make_json_safe(rows[0][0])

        return 0

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


def sql_dataframe_records(sql):
    try:
        columns, rows = execute_sql(sql)

        safe_rows = make_json_safe(rows)

        df = pd.DataFrame(safe_rows, columns=columns)

        return df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


# =====================================================
# HISTORY FUNCTIONS
# =====================================================

def create_history_table():
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100),
                question TEXT,
                sql_query TEXT,
                columns_json JSONB,
                result_json JSONB,
                insight TEXT,
                chart_path TEXT,
                report_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def save_analysis(username, response):
    create_history_table()

    columns = make_json_safe(response.get("columns", []))
    result = make_json_safe(response.get("result", []))

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO analysis_history (
                username,
                question,
                sql_query,
                columns_json,
                result_json,
                insight,
                chart_path,
                report_path
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                username,
                response.get("question", ""),
                response.get("sql", ""),
                Json(columns),
                Json(result),
                response.get("insight", ""),
                response.get("chart_path", ""),
                response.get("report_path", "")
            )
        )

        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_history(username, limit=30):
    create_history_table()

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                question,
                sql_query,
                columns_json,
                result_json,
                insight,
                chart_path,
                report_path,
                created_at
            FROM analysis_history
            WHERE username = %s
            ORDER BY created_at DESC
            LIMIT %s;
            """,
            (username, limit)
        )

        rows = cursor.fetchall()

        history = []

        for row in rows:
            history.append(
                {
                    "id": row[0],
                    "question": row[1],
                    "sql": row[2],
                    "columns": row[3],
                    "result": row[4],
                    "insight": row[5],
                    "chart_path": row[6],
                    "report_path": row[7],
                    "created_at": row[8].isoformat() if row[8] else None
                }
            )

        return history

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def clear_history(username):
    create_history_table()

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM analysis_history
            WHERE username = %s;
            """,
            (username,)
        )

        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =====================================================
# API ROUTES
# =====================================================

@app.get("/")
def home():
    return {
        "message": "Agentic SQL Data Analyst API is running",
        "status": "active"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.post("/login")
def login(request: LoginRequest):
    if request.username == APP_USERNAME and request.password == APP_PASSWORD:
        create_history_table()

        return {
            "success": True,
            "message": "Login successful",
            "username": request.username
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid username or password"
    )


@app.get("/dashboard/metrics")
def dashboard_metrics():
    total_revenue = sql_value(
        "SELECT COALESCE(SUM(quantity * price), 0) FROM order_items;"
    )

    total_orders = sql_value(
        "SELECT COUNT(*) FROM orders;"
    )

    total_customers = sql_value(
        "SELECT COUNT(*) FROM customers;"
    )

    total_products = sql_value(
        "SELECT COUNT(*) FROM products;"
    )

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_products": total_products
    }


@app.get("/dashboard/revenue-by-category")
def revenue_by_category():
    data = sql_dataframe_records(
        """
        SELECT p.category,
               SUM(oi.quantity * oi.price) AS revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue DESC;
        """
    )

    return {
        "data": data
    }


@app.get("/dashboard/top-products")
def top_products():
    data = sql_dataframe_records(
        """
        SELECT p.product_name,
               SUM(oi.quantity * oi.price) AS revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY revenue DESC
        LIMIT 5;
        """
    )

    return {
        "data": data
    }


@app.get("/dashboard/orders-by-status")
def orders_by_status():
    data = sql_dataframe_records(
        """
        SELECT status, COUNT(*) AS total_orders
        FROM orders
        GROUP BY status
        ORDER BY total_orders DESC;
        """
    )

    return {
        "data": data
    }


@app.get("/dashboard/revenue-by-country")
def revenue_by_country():
    data = sql_dataframe_records(
        """
        SELECT c.country,
               SUM(oi.quantity * oi.price) AS revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.country
        ORDER BY revenue DESC
        LIMIT 8;
        """
    )

    return {
        "data": data
    }


@app.post("/query")
def process_query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    response = run_agent(request.question)

    if "error" in response:
        raise HTTPException(
            status_code=500,
            detail=response["error"]
        )

    safe_response = make_json_safe(response)

    save_analysis(request.username, safe_response)

    return safe_response


@app.get("/history/{username}")
def history(username: str):
    data = get_history(username)

    return {
        "history": data
    }


@app.delete("/history/{username}")
def delete_history(username: str):
    clear_history(username)

    return {
        "success": True,
        "message": "History cleared successfully"
    }