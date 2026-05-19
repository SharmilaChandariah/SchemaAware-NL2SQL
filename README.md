# SQLQueryAI

**A Schema-Based Retrieval-Augmented Generation Framework for Enterprise Natural Language to SQL Query Generation**

[![arXiv](https://img.shields.io/badge/arXiv-Paper-red)](https://arxiv.org/abs/REPLACE_WITH_YOUR_ARXIV_ID)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Author:** Sharmila Devi Chandariah — Capgemini Technology Services  
> **Paper:** [SQLQueryAI: A Schema-Based RAG Framework for Enterprise NL-to-SQL](https://arxiv.org/abs/REPLACE_WITH_YOUR_ARXIV_ID)

---

## What is SQLQueryAI?

SQLQueryAI converts plain-English natural language questions into accurate, schema-aware SQL queries using a Retrieval-Augmented Generation (RAG) architecture.

**The problem it solves:** In large enterprises, non-technical users — testers, analysts, business stakeholders — cannot access data without involving backend developers to write SQL queries. This creates a bottleneck of 4 hours to 2 days per request, affecting productivity across dozens of teams simultaneously.

**The key design principle:** SQLQueryAI operates on database *schemas only* — never on actual data records. This enables deployment in regulated enterprise environments (insurance, healthcare, finance) where data privacy requirements prohibit exposing production data to AI systems.

---

## Key Features

- **Schema-only operation** — no access to actual data records; compliant with enterprise data governance
- **RAG pipeline** — retrieves relevant schema fragments, sample queries, and domain context at inference time
- **Domain-agnostic** — customize for any industry by changing knowledge sources, not architecture
- **93.3% accuracy** on 30 real-world enterprise scenarios (83.3% exact match + 10% minor refinement)
- **Enterprise-certified** — design enables formal AI governance review and certification

---

## Architecture

```
PRE-PROCESSING (offline)
├── Schema files (DDL / data dictionary)
├── Sample query library (50+ curated NL→SQL pairs)
└── Domain context templates
        ↓ Embedding Model (e.g., Amazon Titan Embeddings)
        ↓ Vector Database (cosine similarity index)

QUERY GENERATION (online, per user request)
User Input (natural language)
    → Embed query
    → Cosine similarity search → retrieve: schema fragments + sample queries + domain context
    → Augmented prompt → LLM (e.g., Anthropic Claude / OpenAI GPT-4)
    → Generated SQL query → returned to user
```

---

## Quick Start

### Prerequisites
```bash
pip install streamlit openai boto3 langchain chromadb pandas
```

### Setup
```bash
git clone https://github.com/YOUR_USERNAME/SQLQueryAI.git
cd SQLQueryAI
pip install -r requirements.txt
```

### Configuration
1. Add your database schema to `data/schema/`
2. Add sample queries to `data/samples/queries.csv` (format: `natural_language, sql_query`)
3. Add domain context to `data/context/domain_context.txt`
4. Configure your LLM API credentials in `.env`

```env
# .env
LLM_PROVIDER=openai          # or: bedrock, azure
OPENAI_API_KEY=your_key_here
EMBEDDING_MODEL=text-embedding-ada-002
VECTOR_DB=chromadb           # or: pinecone, weaviate
```

### Run
```bash
streamlit run app.py
```

---

## Repository Structure

```
SQLQueryAI/
├── app.py                    # Streamlit UI entry point
├── src/
│   ├── preprocessor.py       # Schema ingestion, embedding, vector DB indexing
│   ├── retriever.py          # Cosine similarity search and context retrieval
│   ├── generator.py          # LLM prompt assembly and SQL generation
│   └── validator.py          # Optional: query validation layer
├── data/
│   ├── schema/               # Your database schema files (DDL, CSV, or data dictionary)
│   ├── samples/
│   │   └── queries.csv       # Sample NL→SQL pairs (50+ recommended)
│   └── context/
│       └── domain_context.txt # Domain-specific context and vocabulary
├── config/
│   └── settings.py           # LLM, embedding model, vector DB configuration
├── tests/
│   └── test_accuracy.py      # Accuracy evaluation framework
├── requirements.txt
└── README.md
```

---

## Domain Customization

SQLQueryAI is domain-agnostic. To adapt to a new domain:

1. **Replace the schema** in `data/schema/` with your domain's database schema
2. **Build a sample library** — create 50+ NL→SQL pairs covering your most common query patterns
3. **Write context templates** — encode your domain vocabulary, entity definitions, and relationship semantics in `data/context/domain_context.txt`

No changes to the core architecture are required.

**Domains validated:**
- ✅ P&C Insurance (deployed as InsureQueryAI at enterprise scale)
- 🔄 Banking (architecture evaluation in progress)
- 🔄 Healthcare (architecture evaluation in progress)

---

## Evaluation Results

Tested on 30 real-world enterprise scenarios (simple / medium / complex):

| Result | Count | Percentage |
|--------|-------|------------|
| Exact match | 25 | 83.3% |
| Minor refinement needed | 3 | 10.0% |
| No match (resolved after prompt tuning) | 2 | 6.7% |
| **Overall accuracy (exact + partial)** | **28/30** | **93.3%** |

---

## Enterprise Deployment Notes

When deploying in regulated environments:

- **Data privacy:** the system never requires access to production data — only schema metadata
- **Governance:** schema-only design enables formal AI risk and security review
- **Scalability:** vector database indexing scales to schemas with 100+ tables
- **LLM flexibility:** the framework is LLM-agnostic; swap providers via `config/settings.py`

---

## Citation

If you use SQLQueryAI in your research or work, please cite:

```bibtex
@article{chandariah2026sqlqueryai,
  title={SQLQueryAI: A Schema-Based Retrieval-Augmented Generation Framework for Enterprise Natural Language to SQL Query Generation},
  author={Chandariah, Sharmila Devi},
  journal={arXiv preprint arXiv:REPLACE_WITH_YOUR_ARXIV_ID},
  year={2026}
}
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Contact

Sharmila Devi Chandariah  
Capgemini Technology Services  
sharmila-devi.chandariah@capgemini.com
