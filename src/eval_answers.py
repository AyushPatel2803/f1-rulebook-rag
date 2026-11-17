"""Test 2: run every test question through the full app and auto-check the answers."""

import json
import time
from pathlib import Path

from ask import ask, MODEL

SPLIT = "practice"  # only switch to "final" once, at the very end
REFUSAL_PHRASES = [
    "don't cover", "do not cover", "doesn't cover", "not covered",
    "couldn't find", "could not find", "doesn't exist", "does not exist",
]

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
    text = answer.lower()

    refused = any(p in text for p in REFUSAL_PHRASES)
    facts_ok = all(any(w.lower() in text for w in group) for group in t["must_have"])
    cited_ok = any(r.lower() in text for r in t["expected_rules"])

    if t["answerable"]:
        check = "FALSE REFUSAL" if refused else ("OK" if facts_ok and cited_ok else "CHECK")
    else:
        check = "REFUSED" if refused else "ANSWERED - CHECK"

    preview = answer[:70].replace("\n", " ")
    print(f'{t["id"]:>3}  {check:<16} facts={"Y" if facts_ok else "N"}  cited={"Y" if cited_ok else "N"}  {preview}')

    results.append({
        "id": t["id"],
        "question": t["question"],
        "category": t["category"],
        "behaviour": t["behaviour"],
        "expected_answer": t["expected_answer"],
        "app_answer": answer,
        "sources": [{"rule": c["rule"], "doc": c["doc"], "pages": c["pages"], "score": round(s, 3)} for c, s in sources],
        "auto_check": check,
        "model": MODEL,
    })
    time.sleep(3)  # space out calls for the free tier

Path("results").mkdir(exist_ok=True)
out = Path(f"results/answers_{SPLIT}.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

answerable = [r for r in results if r["behaviour"] == "answer"]
ok = sum(r["auto_check"] == "OK" for r in answerable)
false_refusals = sum(r["auto_check"] == "FALSE REFUSAL" for r in answerable)
tricks = [r for r in results if r["behaviour"] != "answer"]
refused_tricks = sum(r["auto_check"] == "REFUSED" for r in tricks)

print()
print(f"Real questions auto-passed: {ok}/{len(answerable)}   false refusals: {false_refusals}")
print(f"Trick questions refused: {refused_tricks}/{len(tricks)}")
print(f"Saved every answer to {out}")