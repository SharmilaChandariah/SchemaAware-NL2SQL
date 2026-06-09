# SchemaAware-NL2SQL: Cross-Domain Natural Language to SQL Using Schema-Only Architecture

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![IEEE Keynote](https://img.shields.io/badge/IEEE-Region%204%20Nexus%20Keynote-00629B?logo=ieee)](https://www.msoe.edu/about-msoe/news/details/ieee-students-converge-on-campus-for-2024-nexus/)

> A GenAI-based Text-to-SQL system that generates accurate SQL queries from natural language using **only the database schema** — no hardcoded table knowledge, no sample data, no schema-specific fine-tuning. Designed for enterprise-scale, cross-domain deployment.
---

## Why This Is Different

Most NL-to-SQL systems fail in real enterprise environments because they are:

- **Schema-dependent** — trained or prompted with specific table names and sample rows
- **Domain-locked** — a model built for healthcare cannot handle retail without retraining
- **Brittle at scale** — they break when schemas change or span multiple accounts

This system takes a fundamentally different approach: **the schema is the only input**. The model reads any relational database schema at runtime and generates SQL from first principles, with no prior knowledge of the target database. The same model works across any industry, any schema, without modification.

This architecture was deployed as the **first enterprise-wide GenAI solution** at a major client organization, enabling non-technical users across multiple business units to query data in plain English — eliminating SQL as a data access bottleneck.
---

## Key Features

- **Schema-only inference** — reads your schema structure; requires no sample data
- **Cross-domain** — HR, retail, healthcare, finance: zero modification between domains
- **No fine-tuning** — works out-of-the-box via schema-aware prompt engineering
- **Two input formats** — Python dict or raw SQL DDL
- **Modular** — schema parser, prompt constructor, and SQL generator are fully decoupled
- **Runtime schema switching** — `update_schema()` swaps domains without a new instance

---

## Repository Structure

```
SchemaAware-NL2SQL/
├── src/
│   ├── __init__.py             # Package entry point
│   ├── schema_parser.py        # Parses dict/DDL schema into SchemaContext
│   ├── prompt_constructor.py   # Builds schema-aware prompts (no sample data)
│   ├── sql_generator.py        # Main interface: SchemaAwareNL2SQL class
│   └── utils.py                # SQL cleaning, validation, display helpers
│
├── examples/
│   └── demo.ipynb              # End-to-end demo across 3 domains
│
├── docs/
│   └── architecture.md         # Design decisions and component breakdown
│
├── tests/
│   └── test_sql_generator.py   # Unit tests (pytest)
│
├── .gitignore
├── CITATION.cff                # Enables GitHub "Cite this repository" button
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Installation

```bash
git clone https://github.com/SharmilaChandariah/SchemaAware-NL2SQL.git
cd SchemaAware-NL2SQL
pip install -r requirements.txt
```

Set your API key:
```bash
export OPENAI_API_KEY="sk-..."
```

---

## Quick Start

### Dict schema input

```python
from src.sql_generator import SchemaAwareNL2SQL

schema = {
    "employees": {
        "columns": ["employee_id", "name", "department_id", "salary", "hire_date"],
        "types":   ["INT", "VARCHAR", "INT", "DECIMAL", "DATE"],
        "pk": "employee_id"
    },
    "departments": {
        "columns": ["department_id", "department_name", "location"],
        "types":   ["INT", "VARCHAR", "VARCHAR"],
        "pk": "department_id"
    }
}

fk = [("employees.department_id", "departments.department_id")]

model = SchemaAwareNL2SQL(schema=schema, foreign_keys=fk)
sql = model.generate("List names and salaries of employees in Engineering hired after 2020")
print(sql)
```

```sql
SELECT e.name, e.salary
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE d.department_name = 'Engineering'
  AND e.hire_date > '2020-01-01';
```

### DDL schema input

```python
ddl = """
    CREATE TABLE orders (
        order_id   INT PRIMARY KEY,
        customer_id INT,
        order_date  DATE,
        total       DECIMAL(10,2),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    CREATE TABLE customers (
        customer_id INT PRIMARY KEY,
        name        VARCHAR(100),
        region      VARCHAR(50),
        tier        VARCHAR(20)
    );
"""

model = SchemaAwareNL2SQL(schema=ddl)
sql = model.generate("Total revenue by region for premium customers in Q1 2024")
print(sql)
```

---

## Cross-Domain Portability

The same model, zero modification, works on an entirely different schema:

```python
# Switch domains at runtime — no new instance, no retraining
model.update_schema(healthcare_schema, healthcare_fk)
sql = model.generate("List patients seen by a cardiologist more than twice in 2024")
```

This cross-domain capability — same architecture, same weights, any schema — is the core contribution of this work.

---

## Architecture Overview

```
Natural Language Question
        │
        ▼
┌───────────────────┐
│  SchemaParser     │  Reads any schema (dict or DDL) into a SchemaContext.
│                   │  No sample data stored or used.
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ PromptConstructor │  Builds a structured prompt: schema + FK relationships + question.
│                   │  The prompt contains schema structure only — zero domain hardcoding.
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  LLM Engine       │  Generates SQL from schema context alone.
│  (OpenAI / compat)│  Supports any OpenAI-compatible endpoint.
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Post-Processor   │  Strips markdown, validates SQL structure.
└───────────────────┘
        │
        ▼
    SQL Output
```

See [docs/architecture.md](docs/architecture.md) for a full breakdown.

---

## Comparison with Existing Approaches

| Approach | Schema-Independent | Cross-Domain | No Fine-Tuning | Enterprise-Deployed |
|---|---|---|---|---|
| Traditional NL2SQL (seq2seq) | ✗ | ✗ | ✗ | ✗ |
| Schema-linked models (RAT-SQL, IRNet) | Partial | ✗ | ✗ | ✗ |
| LLM + few-shot prompting | ✗ | Partial | ✓ | Rare |
| **This work (Schema-Only)** | **✓** | **✓** | **✓** | **✓** |

---

## Enterprise Deployment & Recognition

- Deployed as the **first enterprise-wide GenAI solution** at a major client organization, spanning multiple business units
- Only external participant invited to present at the client's internal enterprise innovation meeting
- **Keynote speaker**, [IEEE Region 4 Nexus Conference](https://www.msoe.edu/about-msoe/news/details/ieee-students-converge-on-campus-for-2024-nexus/), Milwaukee School of Engineering, Wisconsin — November 2024

Industry context: Gartner named natural language querying a top enterprise data priority in April 2024. BCG described Text-to-SQL as "high-value but intricate" for enterprise in November 2024. IBM and Oracle both launched commercial NL-to-SQL products that same year. This system was built and deployed enterprise-wide during that same inflection period — before vendor solutions were available off the shelf.

---

## Running Tests

```bash
pytest tests/
```

Tests cover: schema parsing (dict + DDL), primary/foreign key detection, prompt construction, the no-sample-data invariant, SQL cleaning, and syntax validation — all without requiring an API key.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

High-value areas:
- Benchmarking on [Spider 2.0](https://arxiv.org/abs/2411.07763) and [BIRD](https://bird-bench.github.io/)
- Additional LLM backends (Llama, Mistral, Gemini)
- Additional schema input formats (SQLAlchemy, dbt YAML)
- Evaluation harness with execution accuracy metrics

---

## Citation

```bibtex
@software{chandariah2024schemanl2sql,
  author = {Chandariah, Sharmila Devi},
  title  = {SchemaAware-NL2SQL: Cross-Domain Natural Language to SQL Using Schema-Only Architecture},
  year   = {2024},
  url    = {https://github.com/SharmilaChandariah/SchemaAware-NL2SQL},
  note   = {Keynote presentation, IEEE Region 4 Nexus Conference, Milwaukee WI, November 2024}
}
```

A preprint describing the architecture and enterprise deployment results is in preparation for open-access submission.

---

## Related Work

- [Spider 2.0 (2024)](https://arxiv.org/abs/2411.07763) — enterprise NL-to-SQL remains an open challenge
- [BCG: Text-to-SQL for Enterprise (Nov 2024)](https://www.bcg.com/x/the-multiplier/removing-barriers-to-data-with-text-to-sql)
- [Gartner Top Trends in Data & Analytics 2024](https://www.gartner.com/en/newsroom/press-releases/2024-04-25-gartner-identifies-the-top-trends-in-data-and-analytics-for-2024)
- [CIDR 2024: NL2SQL is a Solved Problem... Not!](https://www.cidrdb.org/cidr2024/papers/p74-floratou.pdf)

---

## License

[MIT License](LICENSE)

---

**Sharmila Devi Chandariah** · GenAI Engineer · IEEE Region 4 Nexus Keynote Speaker (2024)  
[@SharmilaChandariah](https://github.com/SharmilaChandariah)
