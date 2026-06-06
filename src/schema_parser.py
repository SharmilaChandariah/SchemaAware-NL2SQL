"""
schema_parser.py
----------------
Parses any relational database schema into a structured SchemaContext object.

Supports two input formats:
  1. Python dict  — {"table_name": {"columns": [...], "types": [...], "pk": "..."}}
  2. SQL DDL string — raw CREATE TABLE statements

The SchemaContext is the sole input to the prompt constructor.
No sample data, no hardcoded domain knowledge is required or used.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class ColumnInfo:
    name: str
    dtype: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: Optional[str] = None  # "other_table.other_column"
    nullable: bool = True


@dataclass
class TableInfo:
    name: str
    columns: list[ColumnInfo] = field(default_factory=list)

    def get_column(self, name: str) -> Optional[ColumnInfo]:
        return next((c for c in self.columns if c.name == name), None)

    def primary_keys(self) -> list[str]:
        return [c.name for c in self.columns if c.is_primary_key]

    def foreign_keys(self) -> list[ColumnInfo]:
        return [c for c in self.columns if c.is_foreign_key]


@dataclass
class SchemaContext:
    """
    A domain-agnostic, structured representation of a relational database schema.
    This is the only context the model needs to generate SQL.
    """
    tables: dict[str, TableInfo] = field(default_factory=dict)
    source: str = "dict"  # "dict" or "ddl"

    def table_names(self) -> list[str]:
        return list(self.tables.keys())

    def summary(self) -> str:
        """Returns a compact human-readable schema summary."""
        lines = []
        for tname, tinfo in self.tables.items():
            col_parts = []
            for col in tinfo.columns:
                tag = ""
                if col.is_primary_key:
                    tag = " [PK]"
                elif col.is_foreign_key:
                    tag = f" [FK -> {col.references}]"
                col_parts.append(f"{col.name} {col.dtype}{tag}")
            lines.append(f"  {tname}({', '.join(col_parts)})")
        return "\n".join(lines)


class SchemaParser:
    """
    Converts raw schema input into a SchemaContext.

    Example (dict input):
        schema_dict = {
            "employees": {
                "columns": ["id", "name", "dept_id", "salary"],
                "types":   ["INT", "VARCHAR", "INT", "DECIMAL"],
                "pk": "id"
            },
            "departments": {
                "columns": ["id", "name"],
                "types":   ["INT", "VARCHAR"],
                "pk": "id"
            }
        }
        foreign_keys = [("employees.dept_id", "departments.id")]

        ctx = SchemaParser.from_dict(schema_dict, foreign_keys)

    Example (DDL input):
        ddl = '''
            CREATE TABLE employees (
                id INT PRIMARY KEY,
                name VARCHAR(100),
                dept_id INT,
                salary DECIMAL(10,2),
                FOREIGN KEY (dept_id) REFERENCES departments(id)
            );
        '''
        ctx = SchemaParser.from_ddl(ddl)
    """

    @staticmethod
    def from_dict(
        schema: dict,
        foreign_keys: Optional[list[tuple[str, str]]] = None
    ) -> SchemaContext:
        """
        Parse schema from a Python dictionary.

        Args:
            schema: dict mapping table name -> {"columns": [...], "types": [...], "pk": "..."}
            foreign_keys: list of ("table.column", "ref_table.ref_column") tuples

        Returns:
            SchemaContext
        """
        fk_map: dict[str, str] = {}
        if foreign_keys:
            for src, ref in foreign_keys:
                fk_map[src.strip()] = ref.strip()

        ctx = SchemaContext(source="dict")

        for table_name, table_def in schema.items():
            columns = table_def.get("columns", [])
            types = table_def.get("types", ["TEXT"] * len(columns))
            pk = table_def.get("pk", "")
            pks = [pk] if isinstance(pk, str) else list(pk)

            table = TableInfo(name=table_name)
            for col_name, col_type in zip(columns, types):
                fk_key = f"{table_name}.{col_name}"
                col = ColumnInfo(
                    name=col_name,
                    dtype=col_type,
                    is_primary_key=(col_name in pks),
                    is_foreign_key=(fk_key in fk_map),
                    references=fk_map.get(fk_key),
                )
                table.columns.append(col)
            ctx.tables[table_name] = table

        return ctx

    @staticmethod
    def from_ddl(ddl: str) -> SchemaContext:
        """
        Parse schema from raw SQL DDL (CREATE TABLE statements).

        Args:
            ddl: SQL DDL string containing one or more CREATE TABLE statements

        Returns:
            SchemaContext
        """
        ctx = SchemaContext(source="ddl")

        # Split into individual CREATE TABLE blocks
        table_blocks = re.findall(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?(\w+)[`\"]?\s*\((.+?)\)\s*;",
            ddl,
            re.IGNORECASE | re.DOTALL,
        )

        for table_name, body in table_blocks:
            table = TableInfo(name=table_name.lower())
            fk_pattern = re.compile(
                r"FOREIGN\s+KEY\s*\((\w+)\)\s+REFERENCES\s+(\w+)\s*\((\w+)\)",
                re.IGNORECASE,
            )
            fk_refs: dict[str, str] = {}
            for match in fk_pattern.finditer(body):
                col, ref_table, ref_col = match.groups()
                fk_refs[col.lower()] = f"{ref_table.lower()}.{ref_col.lower()}"

            pk_inline = re.findall(r"PRIMARY\s+KEY\s*\(([^)]+)\)", body, re.IGNORECASE)
            explicit_pks: set[str] = set()
            for pk_group in pk_inline:
                for pk_col in pk_group.split(","):
                    explicit_pks.add(pk_col.strip().strip("`\"").lower())

            lines = [ln.strip() for ln in body.split(",")]
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if re.match(r"(PRIMARY|FOREIGN|UNIQUE|INDEX|KEY|CONSTRAINT)\s", line, re.IGNORECASE):
                    continue

                parts = line.split()
                if len(parts) < 2:
                    continue

                col_name = parts[0].strip("`\"").lower()
                col_type = parts[1].upper()
                is_pk = ("PRIMARY" in line.upper() and "KEY" in line.upper()) or (col_name in explicit_pks)
                is_fk = col_name in fk_refs

                col = ColumnInfo(
                    name=col_name,
                    dtype=col_type,
                    is_primary_key=is_pk,
                    is_foreign_key=is_fk,
                    references=fk_refs.get(col_name),
                    nullable=("NOT NULL" not in line.upper()),
                )
                table.columns.append(col)

            ctx.tables[table_name.lower()] = table

        return ctx
