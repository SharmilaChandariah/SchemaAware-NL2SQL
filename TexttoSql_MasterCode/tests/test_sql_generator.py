"""
tests/test_sql_generator.py
---------------------------
Unit tests for SchemaAware-NL2SQL components.

Run with:  pytest tests/
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.schema_parser import SchemaParser, SchemaContext, TableInfo, ColumnInfo
from src.prompt_constructor import PromptConstructor
from src.utils import clean_sql_output, validate_sql_syntax


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def hr_schema_dict():
    return {
        "employees": {
            "columns": ["employee_id", "name", "department_id", "salary", "hire_date"],
            "types":   ["INT", "VARCHAR", "INT", "DECIMAL", "DATE"],
            "pk": "employee_id"
        },
        "departments": {
            "columns": ["department_id", "department_name", "manager_id"],
            "types":   ["INT", "VARCHAR", "INT"],
            "pk": "department_id"
        }
    }

@pytest.fixture
def hr_foreign_keys():
    return [("employees.department_id", "departments.department_id")]

@pytest.fixture
def hr_context(hr_schema_dict, hr_foreign_keys):
    return SchemaParser.from_dict(hr_schema_dict, hr_foreign_keys)

@pytest.fixture
def retail_ddl():
    return """
    CREATE TABLE customers (
        customer_id INT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        region VARCHAR(50),
        tier VARCHAR(20)
    );
    CREATE TABLE orders (
        order_id INT PRIMARY KEY,
        customer_id INT,
        order_date DATE,
        total_amount DECIMAL(10,2),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    """


# ---------------------------------------------------------------------------
# SchemaParser tests
# ---------------------------------------------------------------------------

class TestSchemaParserDict:

    def test_parses_table_names(self, hr_context):
        assert "employees" in hr_context.table_names()
        assert "departments" in hr_context.table_names()

    def test_parses_column_names(self, hr_context):
        emp = hr_context.tables["employees"]
        col_names = [c.name for c in emp.columns]
        assert "employee_id" in col_names
        assert "salary" in col_names

    def test_primary_key_detected(self, hr_context):
        emp = hr_context.tables["employees"]
        pk_col = emp.get_column("employee_id")
        assert pk_col is not None
        assert pk_col.is_primary_key is True

    def test_foreign_key_detected(self, hr_context):
        emp = hr_context.tables["employees"]
        fk_col = emp.get_column("department_id")
        assert fk_col is not None
        assert fk_col.is_foreign_key is True
        assert fk_col.references == "departments.department_id"

    def test_non_key_column_is_plain(self, hr_context):
        emp = hr_context.tables["employees"]
        salary = emp.get_column("salary")
        assert salary.is_primary_key is False
        assert salary.is_foreign_key is False

    def test_schema_summary_contains_table_names(self, hr_context):
        summary = hr_context.summary()
        assert "employees" in summary
        assert "departments" in summary


class TestSchemaParserDDL:

    def test_parses_table_names(self, retail_ddl):
        ctx = SchemaParser.from_ddl(retail_ddl)
        assert "customers" in ctx.table_names()
        assert "orders" in ctx.table_names()

    def test_parses_columns(self, retail_ddl):
        ctx = SchemaParser.from_ddl(retail_ddl)
        orders = ctx.tables["orders"]
        col_names = [c.name for c in orders.columns]
        assert "order_id" in col_names
        assert "total_amount" in col_names

    def test_foreign_key_from_ddl(self, retail_ddl):
        ctx = SchemaParser.from_ddl(retail_ddl)
        orders = ctx.tables["orders"]
        fk = orders.get_column("customer_id")
        assert fk is not None
        assert fk.is_foreign_key is True
        assert "customers" in fk.references


# ---------------------------------------------------------------------------
# PromptConstructor tests
# ---------------------------------------------------------------------------

class TestPromptConstructor:

    def test_returns_list_of_messages(self, hr_context):
        pc = PromptConstructor()
        messages = pc.build(hr_context, "How many employees are in each department?")
        assert isinstance(messages, list)
        assert len(messages) == 2

    def test_system_role_present(self, hr_context):
        pc = PromptConstructor()
        messages = pc.build(hr_context, "Test question")
        assert messages[0]["role"] == "system"

    def test_user_message_contains_schema(self, hr_context):
        pc = PromptConstructor()
        messages = pc.build(hr_context, "Test question")
        user_content = messages[1]["content"]
        assert "employees" in user_content
        assert "departments" in user_content

    def test_user_message_contains_question(self, hr_context):
        pc = PromptConstructor()
        question = "List the top 5 highest paid employees"
        messages = pc.build(hr_context, question)
        assert question in messages[1]["content"]

    def test_user_message_contains_fk_relationship(self, hr_context):
        pc = PromptConstructor()
        messages = pc.build(hr_context, "Test")
        assert "department_id" in messages[1]["content"]

    def test_no_sample_data_in_prompt(self, hr_context):
        """Core invariant: prompts must never contain sample/row data."""
        pc = PromptConstructor()
        messages = pc.build(hr_context, "Show employees with salary > 50000")
        full_prompt = " ".join(m["content"] for m in messages)
        # Ensure no hardcoded data values appear
        assert "Engineering" not in full_prompt
        assert "John" not in full_prompt


# ---------------------------------------------------------------------------
# Utils tests
# ---------------------------------------------------------------------------

class TestCleanSqlOutput:

    def test_removes_sql_code_fence(self):
        raw = "```sql\nSELECT * FROM employees;\n```"
        assert clean_sql_output(raw) == "SELECT * FROM employees;"

    def test_removes_plain_code_fence(self):
        raw = "```\nSELECT id FROM users;\n```"
        assert clean_sql_output(raw) == "SELECT id FROM users;"

    def test_passes_clean_sql_through(self):
        sql = "SELECT name, salary FROM employees WHERE salary > 50000;"
        assert clean_sql_output(sql) == sql

    def test_strips_whitespace(self):
        raw = "  \n  SELECT 1;  \n  "
        assert clean_sql_output(raw) == "SELECT 1;"


class TestValidateSqlSyntax:

    def test_valid_select(self):
        ok, msg = validate_sql_syntax("SELECT * FROM employees;")
        assert ok is True

    def test_valid_with_clause(self):
        ok, _ = validate_sql_syntax("WITH cte AS (SELECT 1) SELECT * FROM cte;")
        assert ok is True

    def test_empty_string_invalid(self):
        ok, _ = validate_sql_syntax("")
        assert ok is False

    def test_unbalanced_parens_invalid(self):
        ok, _ = validate_sql_syntax("SELECT (id FROM employees;")
        assert ok is False

    def test_model_failure_signal_invalid(self):
        ok, _ = validate_sql_syntax("-- Cannot generate SQL: schema mismatch")
        assert ok is False

    def test_non_sql_start_invalid(self):
        ok, _ = validate_sql_syntax("Here is the SQL you requested: SELECT 1;")
        assert ok is False
