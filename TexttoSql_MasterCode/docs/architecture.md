# Architecture: Schema-Only NL-to-SQL

## Design Philosophy

Most NL-to-SQL systems are designed around specific schemas or domains. They require either fine-tuning on schema-specific data, or prompts seeded with sample rows. This makes them brittle across domains.

SchemaAware-NL2SQL is built on a single principle: **the schema is sufficient context for SQL generation**. A well-structured relational schema encodes everything an LLM needs — entity names, attribute types, cardinality relationships, and join paths — without any sample data.

## Components

### 1. SchemaParser (`src/schema_parser.py`)

Converts raw schema input into a `SchemaContext` — a domain-agnostic structured representation.

Accepts two formats:
- **Dict input**: `{"table": {"columns": [...], "types": [...], "pk": "..."}}`
- **DDL input**: raw `CREATE TABLE` SQL statements

Output: a `SchemaContext` containing `TableInfo` and `ColumnInfo` objects with primary keys, foreign keys, and type information. No data values are stored or used.

### 2. PromptConstructor (`src/prompt_constructor.py`)

Takes a `SchemaContext` and a natural language question and produces a structured prompt for the LLM.

The prompt contains:
- A system instruction establishing the model's role and constraints
- A schema block: table names, column names, types, PK/FK annotations
- A relationship block: explicit FK join paths
- The natural language question

The prompt contains **no sample data**. This is the architectural invariant that makes the system cross-domain.

### 3. SchemaAwareNL2SQL (`src/sql_generator.py`)

The main public interface. Accepts a schema (dict or DDL), parses it, and exposes a `generate(question)` method. Calls the LLM via OpenAI API (or any compatible endpoint) and returns cleaned SQL.

Also exposes:
- `generate_with_explanation()` — returns the full prompt alongside the SQL, for debugging and transparency
- `update_schema()` — swaps the schema without creating a new instance, enabling multi-tenant or cross-domain switching at runtime
- `schema_summary()` — returns a human-readable schema summary

### 4. Utils (`src/utils.py`)

- `clean_sql_output()` — strips markdown fences from LLM output
- `validate_sql_syntax()` — structural validation without executing the query
- `format_schema_table()` — pretty-prints a schema for CLI/notebook display
- `batch_generate()` — runs multiple questions through a model instance

## Cross-Domain Capability

The cross-domain property emerges from the schema-only architecture. Because the prompt is built entirely from schema structure — and contains no domain-specific artifacts — the LLM reasons about the question in terms of the given schema alone.

This means a model instance loaded with an HR schema can be reloaded with a retail or healthcare schema using `update_schema()`, and the generation behavior is fully governed by the new schema.

## LLM Compatibility

The system uses OpenAI's chat completions API by default. Any endpoint that implements the same interface works:

| Backend | How to use |
|---|---|
| OpenAI (default) | Set `OPENAI_API_KEY` |
| Azure OpenAI | Pass `base_url` and `api_key` to constructor |
| Ollama (local) | Pass `base_url="http://localhost:11434/v1"` |
| Together AI | Pass `base_url` and Together API key |
| LM Studio | Pass `base_url="http://localhost:1234/v1"` |

## Prompt Design

The prompt follows a structured format:

```
[SYSTEM]
You are an expert SQL generator...

[USER]
### Database Schema
Table: employees
  - employee_id INT [PK]
  - name VARCHAR
  - department_id INT [FK -> departments.department_id]
  - salary DECIMAL
  - hire_date DATE

Table: departments
  - department_id INT [PK]
  - department_name VARCHAR

### Relationships (Foreign Keys)
  employees.department_id -> departments.department_id

### Question
List all employees in Engineering hired after 2020

### SQL Query
```

The model returns only the SQL query. The `clean_sql_output()` utility strips any markdown artifacts from the response.
