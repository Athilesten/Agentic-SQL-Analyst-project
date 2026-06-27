"""
api_client.py
Streamlit frontend API client for FastAPI backend.
"""

import requests

API_BASE_URL = "http://127.0.0.1:8000"


def login_api(username, password):
    response = requests.post(
        f"{API_BASE_URL}/login",
        json={
            "username": username,
            "password": password
        }
    )

    if response.status_code == 200:
        return response.json()

    return {
        "success": False,
        "error": response.json().get("detail", "Login failed")
    }


def get_dashboard_metrics():
    response = requests.get(f"{API_BASE_URL}/dashboard/metrics")

    if response.status_code == 200:
        return response.json()

    return None


def get_revenue_by_category():
    response = requests.get(f"{API_BASE_URL}/dashboard/revenue-by-category")

    if response.status_code == 200:
        return response.json().get("data", [])

    return []


def get_top_products():
    response = requests.get(f"{API_BASE_URL}/dashboard/top-products")

    if response.status_code == 200:
        return response.json().get("data", [])

    return []


def get_orders_by_status():
    response = requests.get(f"{API_BASE_URL}/dashboard/orders-by-status")

    if response.status_code == 200:
        return response.json().get("data", [])

    return []


def get_revenue_by_country():
    response = requests.get(f"{API_BASE_URL}/dashboard/revenue-by-country")

    if response.status_code == 200:
        return response.json().get("data", [])

    return []


def run_query_api(username, question):
    response = requests.post(
        f"{API_BASE_URL}/query",
        json={
            "username": username,
            "question": question
        }
    )

    if response.status_code == 200:
        return response.json()

    return {
        "error": response.json().get("detail", "Query failed")
    }


def get_history_api(username):
    response = requests.get(f"{API_BASE_URL}/history/{username}")

    if response.status_code == 200:
        return response.json().get("history", [])

    return []


def clear_history_api(username):
    response = requests.delete(f"{API_BASE_URL}/history/{username}")

    if response.status_code == 200:
        return response.json()

    return {
        "success": False,
        "error": "Unable to clear history"
    }