"""Test 2: run every test question through the full app and auto-check the answers."""

import json
import time
from pathlib import Path

from ask import ask, MODEL
from checks import auto_check, print_summary

SPLIT = "practice"  # only switch to "final" once, at the very end

with open("tests/test_set.json", encoding="utf-8") as f:
    tests = [t for t in json.load(f) if t["split"] == SPLIT]


def ask_with_retry(question, tries=3):
    for attempt in range(tries):
        try:
            return ask(question)
        except Exception as e:
            if attempt == tries - 1:
                return f"ERROR: {e}", []
            time.sleep(20)  # most failures here are Groq's free-tier rate limit


results = []
for t in tests:
    answer, sources = ask_with_retry(t["question"])
    label, facts_ok, cited_ok = auto_check(t, answer)
    preview = answer[:70].replace("\n", " ")
    print(f'{t["id"]:>3}  {label:<16} facts={"Y" if facts_ok else "N"}  cited={"Y" if cited_ok else "N"}  {preview}')

    results.append({
        "id": t["id"],
        "question": t["question"],
        "category": t["category"],
        "behaviour": t["behaviour"],
        "expected_answer": t["expected_answer"],
        "app_answer": answer,
        "sources": [{"rule": c["rule"], "doc": c["doc"], "pages": c["pages"], "score": round(s, 3)} for c, s in sources],
        "auto_check": label,
        "model": MODEL,
    })
    time.sleep(3)  # space out calls for the free tier

Path("results").mkdir(exist_ok=True)
out = Path(f"results/answers_{SPLIT}.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print_summary(results)
print(f"Saved every answer to {out}")