# SchemaAware-NL2SQL: Cross-Domain Natural Language to SQL Using Schema-Only Architecture

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![IEEE Keynote](https://img.shields.io/badge/IEEE-Region%204%20Nexus%20Keynote-00629B?logo=ieee)](https://www.msoe.edu/about-msoe/news/details/ieee-students-converge-on-campus-for-2024-nexus/)

> A GenAI-based Text-to-SQL system that generates accurate SQL queries from natural language using **only the database schema** — no hardcoded table knowledge, no sample queries, no schema-specific fine-tuning required. Designed for enterprise-scale, cross-domain deployment.

---

## Why This Is Different

Most NL-to-SQL systems fail in real enterprise environments because they are:

- **Schema-dependent**: trained or prompted with specific table names and sample data
- **Domain-locked**: a model trained on healthcare data cannot reason about a financial or retail schema without retraining
- **Brittle at scale**: they break when schemas change or when deployed across multiple accounts

This system takes a fundamentally different approach: **the schema is the only input**. The model dynamically parses any database schema at runtime and constructs SQL from first principles, without any prior knowledge of the target database. This makes it deployable across any industry, any schema, without modification.

This architecture was successfully deployed as the **first enterprise-wide GenAI solution** at a major client organization, enabling non-technical users across multiple business units to query data using plain English.

---

## Key Features

- **Schema-only inference**: No hardcoded table/column knowledge. The model reads your schema and reasons from it.
- **Cross-domain**: Works on healthcare, financial, retail, HR, and any other relational schema without modification.
- **No fine-tuning required**: Works out-of-the-box with any schema via schema-aware prompt engineering.
- **Modular architecture**: Schema parser, prompt constructor, and SQL generator are fully decoupled.

---

## Architecture Overview
User Natural Language Question
│
▼
┌─────────────────────────┐
│    Schema Ingestion      │  ← Reads DB schema (tables, columns, types, FK relationships)
└─────────────────────────┘
│
▼
┌─────────────────────────┐
│  Schema-Aware Prompt     │  ← Constructs structured prompt with schema context + NL question
│  Constructor             │     No sample data. No hardcoded domain knowledge.
└─────────────────────────┘
│
▼
┌─────────────────────────┐
│  LLM Reasoning Engine    │  ← Generates SQL using schema context alone
└─────────────────────────┘
│
▼
┌─────────────────────────┐
│  SQL Validation &        │  ← Syntax check + schema alignment verification
│  Post-Processor          │
└─────────────────────────┘
│
▼
SQL Query Output

---

## Repository Structure




---

## Installation

```bash
git clone https://github.com/SharmilaChandariah/TexttoSQL_Files.git
cd TexttoSQL_Files
pip install -r requirements.txt
```

---

## Quick Start

```python
from SQLQueryAI_SchemaAware_Project.sql_generator import SchemaAwareNL2SQL

schema = {
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

foreign_keys = [("employees.department_id", "departments.department_id")]

model = SchemaAwareNL2SQL(schema=schema, foreign_keys=foreign_keys)
question = "List names and salaries of employees in Engineering hired after 2020"
print(model.generate(question))
```

**Output:**
```sql
SELECT e.name, e.salary
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE d.department_name = 'Engineering'
  AND e.hire_date > '2020-01-01';
```

The model correctly inferred the JOIN and filter from the schema alone — with no prior knowledge of the data.

---

## Cross-Domain Portability

The same model, zero modification, works on a completely different schema:

```python
# Switch to a retail schema — no retraining, no re-prompting
retail_schema = {
    "orders":    {"columns": ["order_id", "customer_id", "order_date", "total_amount"], ...},
    "customers": {"columns": ["customer_id", "name", "region", "tier"], ...},
}
model = SchemaAwareNL2SQL(schema=retail_schema, foreign_keys=retail_fk)
sql = model.generate("Show total revenue by region for premium customers in Q1 2024")
```

This cross-domain capability — same architecture, same weights, any schema — is the core technical contribution of this work.

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

- Deployed as the **first enterprise-wide GenAI solution** at a major client organization across multiple business units
- Recognized by senior client leadership; sole external participant invited to present at a client-internal enterprise innovation meeting
- **Keynote speaker**, [IEEE Region 4 Nexus Conference](https://www.msoe.edu/about-msoe/news/details/ieee-students-converge-on-campus-for-2024-nexus/), Milwaukee School of Engineering, Wisconsin — November 2024

Industry context: Gartner named natural language querying a top enterprise data priority in April 2024. BCG described Text-to-SQL as "high-value but intricate" for enterprise in November 2024. IBM and Oracle launched commercial NL-to-SQL products that same year. This system was built and deployed enterprise-wide during that inflection period.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

High-value areas:
- Benchmarking against [Spider 2.0](https://arxiv.org/abs/2411.07763) and [BIRD](https://bird-bench.github.io/) datasets
- Support for additional LLM backends (Llama, Mistral, Gemini)
- Additional schema input formats (JSON Schema, SQLAlchemy, dbt YAML)
- Automated evaluation harness

Open an [Issue](https://github.com/SharmilaChandariah/TexttoSQL_Files/issues) or submit a Pull Request.

---

## Citation

```bibtex
@software{chandariah2024schemanl2sql,
  author = {Chandariah, Sharmila Devi},
  title  = {SchemaAware-NL2SQL: Cross-Domain Natural Language to SQL Using Schema-Only Architecture},
  year   = {2024},
  url    = {https://github.com/SharmilaChandariah/TexttoSQL_Files},
  note   = {Keynote presentation, IEEE Region 4 Nexus Conference, Milwaukee WI, November 2024}
}
```

A preprint describing the architecture and enterprise deployment results has been submitted for open-access publication.

---

## Related Work

- [Spider 2.0 (2024)](https://arxiv.org/abs/2411.07763) — documents the unsolved challenge of enterprise NL-to-SQL
- [BCG: Text-to-SQL for Enterprise (Nov 2024)](https://www.bcg.com/x/the-multiplier/removing-barriers-to-data-with-text-to-sql)
- [Gartner Top Trends in Data & Analytics 2024](https://www.gartner.com/en/newsroom/press-releases/2024-04-25-gartner-identifies-the-top-trends-in-data-and-analytics-for-2024)
- [CIDR 2024: NL2SQL is a Solved Problem... Not!](https://www.cidrdb.org/cidr2024/papers/p74-floratou.pdf)

---

## License

[MIT License](LICENSE)

---

**Sharmila Devi Chandariah** · GenAI Engineer · IEEE Region 4 Nexus Keynote Speaker (2024)  
[@SharmilaChandariah](https://github.com/SharmilaChandariah)
