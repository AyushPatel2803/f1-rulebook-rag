"""Embed every flashcard and save the vectors for search."""

import json
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en-v1.5", cache_folder="models")

cards = []
with open("data/chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        cards.append(json.loads(line))

# include the breadcrumb so a sub-rule can be found by its parent's title
texts = [c["context"] + "\n" + c["text"] for c in cards]

vectors = model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=True)

np.save("data/vectors.npy", vectors)
print("Saved", vectors.shape[0], "cards x", vectors.shape[1], "numbers to data/vectors.npy")