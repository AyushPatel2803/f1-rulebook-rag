"""Ask a question about the 2026 F1 regulations and get an answer with sources."""

import json
import os

import numpy as np
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5", cache_folder="models")
vectors = np.load("data/vectors.npy")

cards = []
with open("data/chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        cards.append(json.loads(line))

MODEL = "openai/gpt-oss-20b"
TOP_K = 3
MIN_SCORE = 0.65  # below this, nothing in the rulebook is close enough to answer from

SYSTEM_PROMPT = """You answer questions about the 2026 FIA Formula 1 Regulations.
Use ONLY the rule excerpts provided. Do not use anything you remember about F1.
Cite the rule number for every claim, like (B1.9.6).
If the excerpts do not answer the question, reply exactly:
"The 2026 regulations provided don't cover that."
Keep answers short and in plain English."""


def search(question):
    q = embedder.encode(question, normalize_embeddings=True)
    scores = vectors @ q
    top = np.argsort(scores)[::-1][:TOP_K]
    return [(cards[i], float(scores[i])) for i in top]


def build_prompt(question, results):
    excerpts = []
    for card, score in results:
        header = f"[{card['rule']}] {card['context']} ({card['doc']}, pages {', '.join(card['pages'])})"
        excerpts.append(header + "\n" + card["text"])
    return "Rule excerpts:\n\n" + "\n\n---\n\n".join(excerpts) + f"\n\nQuestion: {question}"


def ask(question):
    results = search(question)
    if results[0][1] < MIN_SCORE:
        return "I couldn't find anything in the 2026 regulations about that.", results

    reply = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(question, results)},
        ],
        temperature=0,
    )
    return reply.choices[0].message.content, results


# lets the Step 5 test script import ask() without starting this question loop
if __name__ == "__main__":
    while True:
        question = input("\nAsk a rules question (or press Enter to quit): ").strip()
        if not question:
            break
        answer, results = ask(question)
        print()
        print(answer)
        print()
        print("Sources searched:")
        for card, score in results:
            print(f"  {score:.0%}  {card['rule']}  {card['doc']}, pages {', '.join(card['pages'])}")