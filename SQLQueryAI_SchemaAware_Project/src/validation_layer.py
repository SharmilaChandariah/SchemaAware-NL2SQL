
def validate_sql(sql):
    blocked = ["DROP", "DELETE", "TRUNCATE"]

    for keyword in blocked:
        if keyword in sql.upper():
            return False

    return True
