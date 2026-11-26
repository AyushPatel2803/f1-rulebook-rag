"""Test 1: does the right rule reach the AI for each practice question?"""
import json
from collections import Counter

from ask import MIN_SCORE, TOP_K, retrieve, rulebook_words, search, split_question

SPLIT = "practice"
DEPTH = 20  # how far down the normal search to look for the right rule


def rule_matches(rule, expected):
    # an expected "B1.9" also counts if search found a sub-rule like "B1.9.6"
    return any(rule == e or rule.startswith(e + ".") for e in expected)


def find(results, expected):
    return next((n for n, (card, _) in enumerate(results, 1)
                 if rule_matches(card["rule"], expected)), None)


with open("tests/test_set.json", encoding="utf-8") as f:
    tests = [t for t in json.load(f) if t["split"] == SPLIT]
real = [t for t in tests if t["answerable"]]
tricks = [t for t in tests if not t["answerable"]]

hits, totals = Counter(), Counter()
in_depth, from_extras = 0, 0
blocked_real = []

print(f"Real questions ({len(real)}): does the right rule reach the AI?\n")
for t in real:
    normal = search(t["question"], k=DEPTH)
    rank = find(normal, t["expected_rules"])
    best = normal[0][1]
    sent = retrieve(t["question"])
    got = find(sent, t["expected_rules"])
    via_extras = got is not None and got > TOP_K

    totals[t["category"]] += 1
    if got:
        hits[t["category"]] += 1
    if rank:
        in_depth += 1
    if via_extras:
        from_extras += 1
    if best < MIN_SCORE:
        blocked_real.append(t["id"])

    status = "HIT " if got else "miss"
    shown = rank if rank else f">{DEPTH}"
    note = "   <- found by word bank / splitting" if via_extras else ""
    print(f"  {status}  #{t['id']:<3} rank {shown:<4} cards {len(sent):<3} {t['question'][:50]}{note}")

total_hits = sum(hits.values())
print(f"\nRight rule sent to the AI: {total_hits}/{len(real)} ({total_hits / len(real):.0%})")
print(f"  from normal search (top {TOP_K}): {total_hits - from_extras}")
print(f"  added by word bank / splitting: {from_extras}")
print(f"Right rule anywhere in the normal top {DEPTH}: {in_depth}/{len(real)}")
print("By category:")
for cat in sorted(totals):
    print(f"  {cat:<22} {hits[cat]}/{totals[cat]}")

print("\nWord bank fired on:")
for t in tests:
    words = rulebook_words(t["question"])
    if words:
        print(f"  #{t['id']:<3} -> {', '.join(words)}")

print("\nSplit into parts:")
for t in tests:
    parts = split_question(t["question"])
    if len(parts) > 1:
        print(f"  #{t['id']:<3} -> " + "  |  ".join(parts))

blocked_tricks = [t["id"] for t in tricks if search(t["question"])[0][1] < MIN_SCORE]
print(f"\nGate ({MIN_SCORE:.0%}) wrongly blocks real questions: {blocked_real or 'none'}")
print(f"Gate blocks trick questions: {len(blocked_tricks)}/{len(tricks)} {blocked_tricks}")