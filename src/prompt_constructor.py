"""
prompt_constructor.py
---------------------
Builds schema-aware prompts from a SchemaContext and a natural language question.

Core design principle:
    The prompt contains ONLY schema structure — table names, column names,
    data types, and relationships. It contains NO sample data, NO hardcoded
    domain assumptions, and NO schema-specific fine-tuning artifacts.

    This is what makes the system cross-domain: a prompt built from a
    healthcare schema looks structurally identical to one from a retail schema.
    The LLM reasons from structure alone.
"""

from __future__ import annotations
from .schema_parser import SchemaContext


SYSTEM_PROMPT = """You are an expert SQL generator. Your task is to convert natural language questions into syntactically correct SQL queries.

Rules:
1. Use ONLY the tables and columns defined in the schema provided. Do not invent columns or tables.
2. Use proper JOIN syntax based on the foreign key relationships shown.
3. Use table aliases for clarity when joining multiple tables.
4. Return ONLY the SQL query — no explanation, no markdown, no code fences.
5. If the question cannot be answered from the given schema, respond with: -- Cannot generate SQL: [reason]
6. Always use standard ANSI SQL unless the question specifies a dialect.
"""


class PromptConstructor:
    """
    Constructs structured prompts for LLM-based SQL generation.

    The prompt consists of:
        1. A system instruction (role + rules)
        2. Schema context block (tables, columns, types, PKs, FKs)
        3. Relationship summary (foreign key joins)
        4. The natural language question

    No sample data is included. The model must reason from schema structure alone.
    """

    def __init__(self, include_types: bool = True, include_relationships: bool = True):
        self.include_types = include_types
        self.include_relationships = include_relationships

    def build(self, schema: SchemaContext, question: str) -> list[dict]:
        """
        Build a chat-format prompt (list of message dicts for OpenAI-style APIs).

        Args:
            schema: parsed SchemaContext
            question: natural language question from the user

        Returns:
            list of {"role": ..., "content": ...} dicts
        """
        schema_block = self._format_schema(schema)
        relationship_block = self._format_relationships(schema)

        user_content = f"""### Database Schema

{schema_block}
"""
        if relationship_block:
            user_content += f"""
### Relationships (Foreign Keys)

{relationship_block}
"""

        user_content += f"""
### Question

{question}

### SQL Query"""

        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_content},
        ]

    def build_as_string(self, schema: SchemaContext, question: str) -> str:
        """
        Build prompt as a single string (for non-chat LLM APIs).
        """
        messages = self.build(schema, question)
        parts = []
        for msg in messages:
            role = msg["role"].upper()
            parts.append(f"[{role}]\n{msg['content']}")
        return "\n\n".join(parts)

    def _format_schema(self, schema: SchemaContext) -> str:
        lines = []
        for table_name, table in schema.tables.items():
            col_defs = []
            for col in table.columns:
                parts = [col.name]
                if self.include_types:
                    parts.append(col.dtype)
                tags = []
                if col.is_primary_key:
                    tags.append("PK")
                if col.is_foreign_key and col.references:
                    tags.append(f"FK -> {col.references}")
                if tags:
                    parts.append(f"[{', '.join(tags)}]")
                col_defs.append(" ".join(parts))
            lines.append(f"Table: {table_name}")
            for cd in col_defs:
                lines.append(f"  - {cd}")
            lines.append("")
        return "\n".join(lines).strip()

    def _format_relationships(self, schema: SchemaContext) -> str:
        relationships = []
        for table_name, table in schema.tables.items():
            for col in table.columns:
                if col.is_foreign_key and col.references:
                    ref_table, ref_col = col.references.split(".")
                    relationships.append(
                        f"  {table_name}.{col.name} -> {ref_table}.{ref_col}"
                    )
        return "\n".join(relationships)
