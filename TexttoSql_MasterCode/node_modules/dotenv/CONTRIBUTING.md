# Contributing to SchemaAware-NL2SQL

Thank you for your interest in contributing. This project is an open-source implementation of a schema-aware NL-to-SQL architecture and welcomes contributions from researchers, engineers, and practitioners.

## How to Contribute

### Reporting Issues
Open a [GitHub Issue](https://github.com/SharmilaChandariah/SchemaAware-NL2SQL/issues) describing:
- What you expected to happen
- What actually happened
- A minimal reproducible example (schema + question + output)

### Submitting Pull Requests
1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests: `pytest tests/`
5. Open a Pull Request with a clear description of what changed and why

## High-Value Contribution Areas

**Benchmarking**
Evaluate the model on public NL-to-SQL benchmarks and report results:
- [Spider](https://yale-lily.github.io/spider) — cross-domain NL-to-SQL
- [Spider 2.0](https://spider2-sql.github.io/) — enterprise-scale challenge
- [BIRD](https://bird-bench.github.io/) — big realistic databases

**Additional LLM Backends**
The current implementation uses OpenAI. Contributions adding support for:
- Meta Llama (via Ollama or Together AI)
- Google Gemini
- Mistral
- Azure OpenAI (configuration example)

**Schema Input Formats**
Extending `SchemaParser` to accept:
- SQLAlchemy model objects
- dbt schema YAML files
- JSON Schema
- Database introspection (live connection)

**Evaluation Metrics**
A test harness that measures:
- Execution accuracy on sample queries
- Schema coverage (does the SQL reference valid tables/columns?)
- Query complexity distribution

## Code Style
- Follow PEP 8
- Add docstrings to all public functions and classes
- Include tests for new functionality in `tests/`

## Questions
Open an Issue with the label `question` or start a Discussion.
