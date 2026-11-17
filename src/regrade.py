"""Re-score saved answers with the current checks, without calling the AI again."""

import json

from checks import auto_check, print_summary

FILE = "results/answers_practice.json"

with open("tests/test_set.json", encoding="utf-8") as f:
    tests = {t["id"]: t for t in json.load(f)}

with open(FILE, encoding="utf-8") as f:
    results = json.load(f)

for r in results:
    label, facts_ok, cited_ok = auto_check(tests[r["id"]], r["app_answer"])
    r["auto_check"] = label
    preview = r["app_answer"][:70].replace("\n", " ")
    print(f'{r["id"]:>3}  {label:<16} facts={"Y" if facts_ok else "N"}  cited={"Y" if cited_ok else "N"}  {preview}')

with open(FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print_summary(results)