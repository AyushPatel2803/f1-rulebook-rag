"""Show where search goes wrong for the questions it misses."""
import json

import numpy as np

from ask import cards, embedder, vectors

MISSES = [4, 6, 8, 19, 20, 22, 29, 53]
SHOW_CHUNKS = ["C4.1", "B5.7.2"]


def rule_matches(rule, expected):
    return any(rule == e or rule.startswith(e + ".") for e in expected)


with open("tests/test_set.json", encoding="utf-8") as f:
    tests = {t["id"]: t for t in json.load(f)}

for n in MISSES:
    t = tests[n]
    q = embedder.encode(t["question"], normalize_embeddings=True)
    scores = vectors @ q
    order = np.argsort(scores)[::-1]
    rank = next((r for r, i in enumerate(order, 1)
                 if rule_matches(cards[i]["rule"], t["expected_rules"])), None)

    print(f"\n#{n}  {t['question']}")
    print(f"  should hit: {', '.join(t['expected_rules'])}   found at rank: {rank}"
          f"   score: {scores[order[rank - 1]]:.0%}")
    print("  what beat it:")
    for r, i in enumerate(order[:5], 1):
        print(f"    {r}. {scores[i]:.0%}  {cards[i]['rule']}  {cards[i]['title']}")

print("\n\n=== Exactly what the embedder sees ===")
for rule in SHOW_CHUNKS:
    card = next((c for c in cards if c["rule"] == rule), None)
    if card:
        print(f"\n--- {card['id']} ---")
        print(card["context"] + "\n" + card["text"])