#def fix_sql(sql, error):

    # print("SQL Error:", error)

    # corrected_sql = sql.replace(
    #     "total_sales",
    #     "amount"
    # )

    # return corrected_sql
"""
correction_loop.py
------------------
Repairs invalid or failing SQL while preserving strict read-only safety rules.
"""

from textwrap import dedent

from practice.sql_generator import SQLGenerator


def clean_sql_response(response_text: str) -> str:
    """Clean and extract SQL from a correction model response."""
    return SQLGenerator.clean_sql(response_text)


def validate_corrected_sql(sql: str) -> bool:
    """Validate corrected SQL using the same rules as initial generation."""
    return SQLGenerator.validate_sql(sql)


def call_correction_model(generator, prompt: str) -> str:
    """
    Call the configured model through the SQL generator.

    Supports:
    - Current SQLGenerator.call_gemini_raw()
    - google-genai client + model_name
    - Older model.generate_content() style
    """
    if not prompt or not prompt.strip():
        raise ValueError("Correction prompt cannot be empty.")

    if hasattr(generator, "call_gemini_raw"):
        return generator.call_gemini_raw(prompt)

    if hasattr(generator, "client") and hasattr(generator, "model_name"):
        response = generator.client.models.generate_content(
            model=generator.model_name,
            contents=prompt
        )

        response_text = getattr(response, "text", None)

        if not response_text:
            raise ValueError("Correction model returned an empty response.")

        return response_text.strip()

    if hasattr(generator, "model"):
        response = generator.model.generate_content(prompt)
        response_text = getattr(response, "text", None)

        if not response_text:
            raise ValueError("Correction model returned an empty response.")

        return response_text.strip()

    raise AttributeError(
        "Unsupported SQL generator. Expected call_gemini_raw(), "
        "client + model_name, or model.generate_content()."
    )


def build_correction_prompt(
    question: str,
    wrong_sql: str,
    error_message: str
) -> str:
    """Build a strict SQL correction prompt."""
    return dedent(
        f"""
        You are a senior PostgreSQL SQL correction assistant.

        Your task is to fix the SQL query so it correctly answers the user's
        business question and runs safely against the provided schema.

        User question:
        {question}

        SQL that failed:
        {wrong_sql}

        Error or validation message:
        {error_message}

        Database schema:
        - customers(customer_id, country, signup_date)
        - products(product_id, product_name, category)
        - orders(order_id, customer_id, order_date, status)
        - order_items(order_id, product_id, quantity, price)

        Mandatory rules:
        - Return only the corrected SQL.
        - Do not include explanations, comments, markdown, or code fences.
        - Use PostgreSQL syntax.
        - Use only read-only SELECT queries.
        - WITH ... SELECT is allowed.
        - Do not use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE,
          REPLACE, MERGE, GRANT, REVOKE, CALL, or EXEC.
        - Do not generate multiple SQL statements.
        - End the SQL with exactly one semicolon.
        """
    ).strip()


def fix_sql(generator, question: str, wrong_sql: str, error_message: str) -> str:
    """
    Correct an invalid SQL query and validate the corrected result.

    Raises:
        RuntimeError: when correction fails or returns unsafe SQL.
    """
    if not question or not question.strip():
        raise ValueError("Question is required for SQL correction.")

    if not wrong_sql or not wrong_sql.strip():
        raise ValueError("Wrong SQL is required for SQL correction.")

    prompt = build_correction_prompt(question, wrong_sql, error_message)

    try:
        response_text = call_correction_model(generator, prompt)
        corrected_sql = clean_sql_response(response_text)
        validate_corrected_sql(corrected_sql)

        return corrected_sql

    except Exception as exc:
        raise RuntimeError(f"SQL correction failed: {exc}") from exc