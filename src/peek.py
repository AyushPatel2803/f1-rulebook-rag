import json

pages = []
with open("data/pages_clean.jsonl", encoding="utf-8") as f:
    for line in f:
        pages.append(json.loads(line))

for p in pages:
    for line in p["text"].splitlines():
        if line.strip().upper().startswith("APPENDIX"):
            print(p["doc"][:9], "|", p["label"], "|", repr(line.strip()))

print()
for p in pages:
    if p["label"] in ("C189", "C190"):
        print("=====", p["label"])
        print(p["text"][:400])