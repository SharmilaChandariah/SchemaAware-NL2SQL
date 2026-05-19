
import json
from src.pipeline import generate_sql
from src.evaluation_engine import exact_match

with open("evaluation/scenarios.json") as f:
    scenarios = json.load(f)

passed = 0

for scenario in scenarios:
    generated = generate_sql(scenario["scenario"])

    if exact_match(scenario["expected_sql"], generated):
        passed += 1

print(f"Passed: {passed}/{len(scenarios)}")
