"""
agent_controller.py
-------------------
Coordinates the natural-language analytics workflow:
question validation, SQL generation, SQL validation, execution, correction,
insight generation, chart generation, report export, and memory retrieval.
"""

import logging
import socket
from typing import Any, Dict, List, Optional, Tuple

from agent1.chart_generator import generate_chart
from agent1.correction_loop import fix_sql
from agent1.export_report import export_session
from agent1.insights import generate_insights
from agent1.memory import get_history, save_message
from agent1.tools import execute_sql

from practice.sql_generator import SQLGenerator
from practice.sql_validator import validate_sql


logger = logging.getLogger(__name__)

BUSINESS_QUERY_KEYWORDS = {
    "show", "list", "total", "count", "revenue", "sales", "product",
    "products", "customer", "customers", "order", "orders", "category",
    "country", "highest", "lowest", "average", "maximum", "minimum",
    "top", "latest", "status", "spending", "purchase", "purchased",
    "quantity", "price", "value", "trend", "summary"
}


def is_business_query(question: str) -> bool:
    """Return True when a question appears related to the available business data."""
    if not question:
        return False

    question_lower = question.lower()
    return any(keyword in question_lower for keyword in BUSINESS_QUERY_KEYWORDS)


def is_network_error(error: Exception) -> bool:
    """Detect common network and DNS failures from model/API calls."""
    error_text = str(error).lower()

    return (
        isinstance(error, socket.gaierror)
        or "getaddrinfo failed" in error_text
        or "name resolution" in error_text
        or "dns" in error_text
        or "connection" in error_text
        or "timed out" in error_text
        or "timeout" in error_text
        or "network" in error_text
    )


def error_response(message: str, technical_detail: Optional[str] = None) -> Dict[str, Any]:
    """Create a consistent error response."""
    response = {"error": message}

    if technical_detail:
        response["technical_detail"] = technical_detail

    return response


def normalize_question(question: str) -> str:
    """Clean user input before processing."""
    return " ".join(question.strip().split())


def validate_or_correct_sql(
    generator: SQLGenerator,
    question: str,
    sql: str,
    validation_message: str
) -> str:
    """Attempt to correct SQL after validation failure."""
    logger.info("SQL validation failed. Attempting correction: %s", validation_message)

    corrected_sql = fix_sql(
        generator=generator,
        question=question,
        wrong_sql=sql,
        error_message=validation_message
    )

    is_valid, message = validate_sql(corrected_sql)

    if not is_valid:
        raise ValueError(f"Corrected SQL is still invalid: {message}")

    return corrected_sql


def execute_with_correction(
    generator: SQLGenerator,
    question: str,
    sql: str
) -> Tuple[str, List[str], List[tuple]]:
    """Execute SQL and attempt one correction pass if execution fails."""
    try:
        columns, result = execute_sql(sql)
        return sql, columns, result

    except Exception as execution_error:
        logger.warning("SQL execution failed. Attempting correction: %s", execution_error)

        corrected_sql = fix_sql(
            generator=generator,
            question=question,
            wrong_sql=sql,
            error_message=str(execution_error)
        )

        is_valid, message = validate_sql(corrected_sql)

        if not is_valid:
            raise ValueError(
                f"Corrected SQL after execution error is invalid: {message}"
            )

        columns, result = execute_sql(corrected_sql)
        return corrected_sql, columns, result


def build_success_response(
    question: str,
    sql: str,
    columns: List[str],
    result: List[tuple],
    insight: str,
    chart_path: Optional[str],
    report_path: Optional[str],
    history: List[Any]
) -> Dict[str, Any]:
    """Create a consistent successful analysis response."""
    return {
        "question": question,
        "sql": sql,
        "columns": columns,
        "result": result,
        "insight": insight,
        "chart_path": chart_path,
        "report_path": report_path,
        "history": history
    }


def process_question(question: str) -> Dict[str, Any]:
    """Run the full analytics workflow for one user question."""
    if not question or not question.strip():
        return error_response("Please enter a valid business question.")

    question = normalize_question(question)

    if not is_business_query(question):
        return error_response(
            "This does not look like a question about the available business data. "
            "Try asking something like 'show revenue by category' or "
            "'show top 5 products by revenue'."
        )

    try:
        save_message(question)
    except Exception as exc:
        logger.warning("Unable to save question to memory: %s", exc)

    try:
        generator = SQLGenerator()
        sql = generator.generate_sql(question)

    except Exception as exc:
        if is_network_error(exc):
            return error_response(
                "The AI service is not reachable right now. Please check internet, "
                "DNS, VPN/proxy settings, and the configured API key.",
                technical_detail=str(exc)
            )

        return error_response(
            "Unable to generate SQL for this question.",
            technical_detail=str(exc)
        )

    try:
        is_valid, validation_message = validate_sql(sql)

        if not is_valid:
            sql = validate_or_correct_sql(
                generator=generator,
                question=question,
                sql=sql,
                validation_message=validation_message
            )

    except Exception as exc:
        return error_response(
            "SQL validation failed and automatic correction was unsuccessful.",
            technical_detail=str(exc)
        )

    try:
        sql, columns, result = execute_with_correction(generator, question, sql)

    except Exception as exc:
        return error_response(
            "The query could not be executed after automatic correction.",
            technical_detail=str(exc)
        )

    try:
        insight = generate_insights(question, columns, result)
    except Exception as exc:
        logger.warning("Insight generation failed: %s", exc)
        insight = "The query ran successfully, but an insight summary could not be generated."

    try:
        chart_path = generate_chart(question, columns, result)
    except Exception as exc:
        logger.warning("Chart generation failed: %s", exc)
        chart_path = None

    try:
        report_path = export_session(
            question=question,
            sql=sql,
            columns=columns,
            result=result,
            insight=insight,
            chart_path=chart_path
        )
    except TypeError:
        report_path = export_session(
            question,
            sql,
            columns,
            result,
            insight,
            chart_path
        )
    except Exception as exc:
        logger.warning("Report export failed: %s", exc)
        report_path = None

    try:
        history = get_history()
    except Exception as exc:
        logger.warning("Unable to fetch conversation history: %s", exc)
        history = []

    return build_success_response(
        question=question,
        sql=sql,
        columns=columns,
        result=result,
        insight=insight,
        chart_path=chart_path,
        report_path=report_path,
        history=history
    )