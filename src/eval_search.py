"""Test 1: does search find the right rule for each practice question?"""
import json
from collections import Counter

from ask import MIN_SCORE, TOP_K, search

SPLIT = "practice"
DEPTH = 20  # how far down the list to look for the right rule


def rule_matches(rule, expected):
    # an expected "B1.9" also counts if search found a sub-rule like "B1.9.6"
    return any(rule == e or rule.startswith(e + ".") for e in expected)


with open("tests/test_set.json", encoding="utf-8") as f:
    tests = [t for t in json.load(f) if t["split"] == SPLIT]
real = [t for t in tests if t["answerable"]]
tricks = [t for t in tests if not t["answerable"]]

hits, totals = Counter(), Counter()
in_depth = 0
blocked_real = []

print(f"Real questions ({len(real)}): where the right rule landed\n")
for t in real:
    results = search(t["question"], k=DEPTH)
    best = results[0][1]
    rank = next((n for n, (card, _) in enumerate(results, 1)
                 if rule_matches(card["rule"], t["expected_rules"])), None)

    totals[t["category"]] += 1
    if rank and rank <= TOP_K:
        hits[t["category"]] += 1
    if rank:
        in_depth += 1
    if best < MIN_SCORE:
        blocked_real.append(t["id"])

    status = "HIT " if rank and rank <= TOP_K else "miss"
    shown = rank if rank else f">{DEPTH}"
    print(f"  {status}  #{t['id']:<3} rank {shown:<4} best {best:.0%}  {t['question'][:60]}")

total_hits = sum(hits.values())
print(f"\nRight rule in top {TOP_K}: {total_hits}/{len(real)} ({total_hits / len(real):.0%})")
print(f"Right rule anywhere in the top {DEPTH}: {in_depth}/{len(real)}")
print("By category:")
for cat in sorted(totals):
    print(f"  {cat:<22} {hits[cat]}/{totals[cat]}")

blocked_tricks = [t["id"] for t in tricks if search(t["question"])[0][1] < MIN_SCORE]
print(f"\nGate ({MIN_SCORE:.0%}) wrongly blocks real questions: {blocked_real or 'none'}")
print(f"Gate blocks trick questions: {len(blocked_tricks)}/{len(tricks)} {blocked_tricks}")