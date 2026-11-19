"""Re-ask only some questions and update the saved answers, to save Groq tokens.

Usage: python src/redo.py 4 20 29
"""
import json
import sys
import time

from ask import ask

PATH = "results/answers_practice.json"
PAUSE = 30  # top-8 questions cost ~5K tokens and Groq allows 8K per minute
ids = {int(a) for a in sys.argv[1:]}

with open(PATH, encoding="utf-8") as f:
    rows = json.load(f)

todo = [r for r in rows if r["id"] in ids]
print(f"{len(todo)} answers to redo")
for r in todo:
    for attempt in range(3):
        try:
            answer, results = ask(r["question"])
            break
        except Exception as e:
            print(f"  #{r['id']} attempt {attempt + 1} failed: {str(e)[:120]}")
            time.sleep(60)  # a per-minute limit clears after a minute
    else:
        print("  still failing, probably the daily limit, so stopping here")
        break

    r["app_answer"] = answer
    r["sources"] = [{"rule": c["rule"], "doc": c["doc"], "pages": c["pages"], "score": round(s, 3)}
                    for c, s in results]
    print(f"  #{r['id']} done")
    time.sleep(PAUSE)

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)