"""Compare two eval runs question by question and show only what changed."""
import json

from checks import auto_check

OLD = "results/hints_answers_practice.json"
NEW = "results/answers_practice.json"


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {r["id"]: r for r in data}


with open("tests/test_set.json", encoding="utf-8") as f:
    tests = {t["id"]: t for t in json.load(f)}

old, new = load(OLD), load(NEW)
for i in sorted(new):
    before, after = old[i]["app_answer"], new[i]["app_answer"]
    label_before = auto_check(tests[i], before)[0]
    label_after = auto_check(tests[i], after)[0]
    if label_before != label_after:
        print(f"\n#{i}  {label_before}  ->  {label_after}   {tests[i]['question']}")
        print("  BEFORE:", before.replace("\n", " ")[:300])
        print("  AFTER: ", after.replace("\n", " ")[:300])