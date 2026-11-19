"""Re-ask only the questions that failed with an error last run (e.g. Groq's daily limit)."""
import json
import time

from ask import ask

PATH = "results/answers_practice.json"

with open(PATH, encoding="utf-8") as f:
    rows = json.load(f)

todo = [r for r in rows if r["app_answer"].startswith("ERROR")]
print(f"{len(todo)} answers to redo")
for r in todo:
    try:
        answer, results = ask(r["question"])
    except Exception as e:
        # the daily limit hasn't reset yet, so stop now instead of burning more requests
        print(f"  #{r['id']} still failing: {str(e)[:120]}")
        break
    r["app_answer"] = answer
    r["sources"] = [{"rule": c["rule"], "doc": c["doc"], "pages": c["pages"], "score": round(s, 3)}
                    for c, s in results]
    print(f"  #{r['id']} done")
    time.sleep(3)

# save whatever got done, even if we stopped early
with open(PATH, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False) 