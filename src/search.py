"""Ask a question and print the 3 flashcards closest in meaning."""

import json
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en-v1.5", cache_folder="models")
vectors = np.load("data/vectors.npy")

cards = []
with open("data/chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        cards.append(json.loads(line))

while True:
    question = input("\nAsk a rules question (or press Enter to quit): ").strip()
    if not question:
        break

    q = model.encode(question, normalize_embeddings=True)
    scores = vectors @ q
    top3 = np.argsort(scores)[::-1][:3]

    for rank, i in enumerate(top3, start=1):
        card = cards[i]
        print()
        print(f"#{rank}  {scores[i]:.0%}  |  {card['rule']}  {card['title']}  |  {card['doc']}, pages {', '.join(card['pages'])}")
        print("   ", card["text"][:250].replace("\n", " "))