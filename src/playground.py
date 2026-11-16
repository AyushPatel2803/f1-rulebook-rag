from sentence_transformers import SentenceTransformer

# cache_folder keeps the model download on D: inside the project, not on C:
model = SentenceTransformer("BAAI/bge-small-en-v1.5", cache_folder="models")

cards = [
    "A car released from the pit stop in an unsafe condition gets a penalty.",
    "Drivers who fail to set a lap time in qualifying are unclassified.",
    "The podium ceremony takes place after the race.",
]
question = "question = Can a team let their car leave its box when it's not safe to?"

card_spots = model.encode(cards, normalize_embeddings=True)
question_spot = model.encode(question, normalize_embeddings=True)

print("Each card became", len(card_spots[0]), "numbers. First 5 of card 1:")
print(card_spots[0][:5])
print()

scores = card_spots @ question_spot
for card, score in zip(cards, scores):
        print(f"{score:.0%}", "|", card)