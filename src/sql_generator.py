"""
sql_generator.py
----------------
Main entry point for SchemaAware-NL2SQL.

SchemaAwareNL2SQL accepts a schema (dict or DDL string), parses it into a
SchemaContext, and generates SQL from natural language questions using an LLM.

The schema is the ONLY context given to the model. No sample data, no
hardcoded domain knowledge. The same instance works across any industry or
database without modification.

Supported LLM backends:
    - OpenAI (default): gpt-4o, gpt-4-turbo, gpt-3.5-turbo
    - Azure OpenAI
    - Any OpenAI-compatible endpoint (Ollama, LM Studio, Together AI, etc.)
"""

from __future__ import annotations
import os
from typing import Optional, Union

from .schema_parser import SchemaParser, SchemaContext
from .prompt_constructor import PromptConstructor
from .utils import clean_sql_output, validate_sql_syntax


class SchemaAwareNL2SQL:
    """
    Cross-domain NL-to-SQL generator using schema-only architecture.

    Parameters
    ----------
    schema : dict or str
        Either a Python dict describing the schema, or a raw SQL DDL string.
        See SchemaParser for accepted formats.
    foreign_keys : list of (str, str), optional
        Foreign key relationships as ("table.column", "ref_table.ref_column") pairs.
        Required when using dict input; automatically parsed from DDL.
    model : str
        LLM model name. Default: "gpt-4o"
    api_key : str, optional
        OpenAI API key. Falls back to OPENAI_API_KEY environment variable.
    base_url : str, optional
        Override the API base URL for Azure OpenAI or compatible endpoints.
    temperature : float
        Sampling temperature. Default 0.0 for deterministic SQL output.

    Examples
    --------
    Basic usage with dict schema:

        schema = {
            "employees": {
                "columns": ["id", "name", "dept_id", "salary", "hire_date"],
                "types":   ["INT", "VARCHAR", "INT", "DECIMAL", "DATE"],
                "pk": "id"
            },
            "departments": {
                "columns": ["id", "name"],
                "types":   ["INT", "VARCHAR"],
                "pk": "id"
            }
        }
        fk = [("employees.dept_id", "departments.id")]

        model = SchemaAwareNL2SQL(schema=schema, foreign_keys=fk)
        sql = model.generate("List all employees in Engineering hired after 2020")
        print(sql)

    Usage with DDL string:

        ddl = '''
            CREATE TABLE orders (
                order_id INT PRIMARY KEY,
                customer_id INT,
                order_date DATE,
                total DECIMAL(10,2),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
            CREATE TABLE customers (
                customer_id INT PRIMARY KEY,
                name VARCHAR(100),
                region VARCHAR(50)
            );
        '''
        model = SchemaAwareNL2SQL(schema=ddl)
        sql = model.generate("Total revenue by region for Q2 2024")
    """

    def __init__(
        self,
        schema: Union[dict, str],
        foreign_keys: Optional[list[tuple[str, str]]] = None,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.0,
    ):
        # Parse schema
        if isinstance(schema, str):
            self.schema_context: SchemaContext = SchemaParser.from_ddl(schema)
        elif isinstance(schema, dict):
            self.schema_context = SchemaParser.from_dict(schema, foreign_keys)
        elif isinstance(schema, SchemaContext):
            self.schema_context = schema
        else:
            raise ValueError("schema must be a dict, DDL string, or SchemaContext object.")

        self.model = model
        self.temperature = temperature
        self._prompt_constructor = PromptConstructor()

        # Lazy-load OpenAI client
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError(
                    "openai package is required. Install with: pip install openai"
                )
            kwargs = {"api_key": self._api_key}
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def generate(self, question: str) -> str:
        """
        Generate a SQL query from a natural language question.

        Parameters
        ----------
        question : str
            Natural language question to convert to SQL.

        Returns
        -------
        str
            A valid SQL query string.
        """
        messages = self._prompt_constructor.build(self.schema_context, question)
        client = self._get_client()

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=1024,
        )

        raw_output = response.choices[0].message.content.strip()
        return clean_sql_output(raw_output)

    def generate_with_explanation(self, question: str) -> dict:
        """
        Generate SQL along with the prompt context used — useful for debugging
        and for demonstrating transparency in how the model reasons.

        Returns
        -------
        dict with keys: "question", "schema_summary", "prompt", "sql"
        """
        messages = self._prompt_constructor.build(self.schema_context, question)
        sql = self.generate(question)

        return {
            "question": question,
            "schema_summary": self.schema_context.summary(),
            "prompt": messages,
            "sql": sql,
        }

    def schema_summary(self) -> str:
        """Return a human-readable summary of the loaded schema."""
        return self.schema_context.summary()

    def update_schema(
        self,
        schema: Union[dict, str],
        foreign_keys: Optional[list[tuple[str, str]]] = None,
    ) -> None:
        """
        Replace the current schema with a new one.
        Enables cross-domain switching without creating a new instance.
        """
        if isinstance(schema, str):
            self.schema_context = SchemaParser.from_ddl(schema)
        else:
            self.schema_context = SchemaParser.from_dict(schema, foreign_keys)
