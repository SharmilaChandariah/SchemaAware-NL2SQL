
from src.schema_ingestion import load_schema
from src.prompt_builder import build_prompt
from src.llm_executor import execute_prompt
from src.rag_pipeline import index_examples, retrieve_examples

EXAMPLES = [
    "Find policies with no driver",
    "Find claims above 10000"
]

index_examples(EXAMPLES)

def generate_sql(user_query):

    schema = load_schema(
        "datasets/synthetic_insurance_schema.sql"
    )

    examples = retrieve_examples(user_query)

    prompt = build_prompt(
        user_query=user_query,
        schema=schema,
        examples="\n".join(examples)
    )

    return execute_prompt(prompt)
