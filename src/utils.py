"""
utils.py
--------
Utility functions for SQL output cleaning, validation, and formatting.
"""

from __future__ import annotations
import re


def clean_sql_output(raw: str) -> str:
    """
    Strip markdown code fences and extra whitespace from LLM SQL output.

    LLMs often wrap SQL in ```sql ... ``` blocks even when instructed not to.
    This function cleans that up to return a bare SQL string.

    Args:
        raw: Raw string output from the LLM

    Returns:
        Clean SQL string
    """
    # Remove ```sql ... ``` or ``` ... ``` fences
    raw = re.sub(r"```(?:sql)?\s*", "", raw, flags=re.IGNORECASE)
    raw = raw.replace("```", "")

    # Remove leading/trailing whitespace and blank lines
    lines = [ln.rstrip() for ln in raw.strip().splitlines()]
    return "\n".join(lines).strip()


def validate_sql_syntax(sql: str) -> tuple[bool, str]:
    """
    Basic structural validation of a SQL query.

    Checks for common indicators of malformed output without executing the query.
    For full validation, execute against a real or in-memory database.

    Args:
        sql: SQL string to validate

    Returns:
        (is_valid: bool, message: str)
    """
    if not sql or not sql.strip():
        return False, "Empty SQL output."

    sql_upper = sql.upper().strip()

    # Must start with a valid SQL keyword
    valid_starts = ("SELECT", "WITH", "INSERT", "UPDATE", "DELETE", "CREATE", "--")
    if not any(sql_upper.startswith(kw) for kw in valid_starts):
        return False, f"SQL does not start with a recognized keyword. Got: {sql[:40]}"

    # Check balanced parentheses
    if sql.count("(") != sql.count(")"):
        return False, "Unbalanced parentheses in SQL."

    # Check for the LLM's failure signal
    if sql_upper.startswith("-- CANNOT GENERATE"):
        return False, f"Model could not generate SQL: {sql}"

    return True, "OK"


def format_schema_table(schema_context) -> str:
    """
    Format a SchemaContext as a printable table for CLI/notebook display.

    Args:
        schema_context: SchemaContext object

    Returns:
        Formatted string
    """
    lines = []
    sep = "-" * 60
    for table_name, table in schema_context.tables.items():
        lines.append(sep)
        lines.append(f"  TABLE: {table_name.upper()}")
        lines.append(sep)
        for col in table.columns:
            tags = []
            if col.is_primary_key:
                tags.append("PK")
            if col.is_foreign_key:
                tags.append(f"FK -> {col.references}")
            tag_str = f"  [{', '.join(tags)}]" if tags else ""
            lines.append(f"  {col.name:<25} {col.dtype:<15}{tag_str}")
        lines.append("")
    return "\n".join(lines)


def batch_generate(model, questions: list[str]) -> list[dict]:
    """
    Run multiple questions through the model and return results.

    Args:
        model: SchemaAwareNL2SQL instance
        questions: list of natural language questions

    Returns:
        list of {"question": str, "sql": str, "valid": bool} dicts
    """
    results = []
    for q in questions:
        try:
            sql = model.generate(q)
            valid, msg = validate_sql_syntax(sql)
            results.append({"question": q, "sql": sql, "valid": valid, "message": msg})
        except Exception as e:
            results.append({"question": q, "sql": "", "valid": False, "message": str(e)})
    return results
