"""Test 1: does search find the right rule for each test question?"""

import json
from collections import Counter

import numpy as np
from sentence_transformers import SentenceTransformer

SPLIT = "practice"  # only switch to "final" once, at the very end
TOP_K = 3
MIN_SCORE = 0.65

model = SentenceTransformer("BAAI/bge-small-en-v1.5", cache_folder="models")
vectors = np.load("data/vectors.npy")

cards = []
with open("data/chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        cards.append(json.loads(line))

with open("tests/test_set.json", encoding="utf-8") as f:
    tests = [t for t in json.load(f) if t["split"] == SPLIT]


def rule_matches(rule, expected):
    # "B5.12" should count "B5.12.3" as a hit, but not "B5.120"
    return any(rule == e or rule.startswith(e + ".") for e in expected)


hits = Counter()
totals = Counter()
blocked = 0
tricks = 0

for t in tests:
    q = model.encode(t["question"], normalize_embeddings=True)
    scores = vectors @ q
    top = np.argsort(scores)[::-1][:TOP_K]
    found = [cards[i]["rule"] for i in top]
    best = float(scores[top[0]])

    if t["answerable"]:
        ok = any(rule_matches(r, t["expected_rules"]) for r in found)
        totals[t["category"]] += 1
        hits[t["category"]] += ok
        status = "HIT " if ok else "MISS"
    else:
        tricks += 1
        if best < MIN_SCORE:
            blocked += 1
            status = "GATE"
        else:
            status = "PASS"

    print(f'{t["id"]:>3}  {status}  {best:.0%}  {t["category"]:<16} found: {", ".join(found)}')

print()
total_hits = sum(hits.values())
total = sum(totals.values())
print(f"Search found the right rule: {total_hits}/{total} ({total_hits / total:.0%})")
for cat in totals:
    print(f"   {cat:<16} {hits[cat]}/{totals[cat]}")
print(f"Trick questions blocked by the 65% gate: {blocked}/{tricks}")