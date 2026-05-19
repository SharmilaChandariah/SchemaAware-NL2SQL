
def build_prompt(user_query, schema, examples):

    return f'''
    You are a SQL generation engine.

    Rules:
    - Use only provided schema.
    - Do not hallucinate columns.
    - Generate optimized SQL.
    - Return SQL only.

    Schema:
    {schema}

    Examples:
    {examples}

    User Query:
    {user_query}
    '''
