"""
SchemaAware-NL2SQL
==================
Cross-domain Natural Language to SQL using schema-only architecture.

No hardcoded table knowledge. No sample queries. No schema-specific fine-tuning.
The model reads any relational schema at runtime and generates SQL from first principles.

Usage:
    from src.sql_generator import SchemaAwareNL2SQL

    model = SchemaAwareNL2SQL(schema=schema_dict, foreign_keys=fk_list)
    sql = model.generate("Show all employees in Engineering hired after 2020")
"""

from .sql_generator import SchemaAwareNL2SQL
from .schema_parser import SchemaParser, SchemaContext
from .prompt_constructor import PromptConstructor

__version__ = "1.0.0"
__author__ = "Sharmila Devi Chandariah"
__all__ = ["SchemaAwareNL2SQL", "SchemaParser", "SchemaContext", "PromptConstructor"]
