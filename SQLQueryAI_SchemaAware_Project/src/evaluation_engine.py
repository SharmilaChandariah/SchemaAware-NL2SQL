
def exact_match(expected, actual):
    return expected.strip().lower() == actual.strip().lower()

def partial_match(expected, actual):
    return expected.lower() in actual.lower()
