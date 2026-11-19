"""Pull the rulebook's own vocabulary: its definition sections and abbreviations."""
import json
import re
from collections import Counter

# the definitions live in the first appendix of each section
DEFINITION_APPENDICES = {"Appendix A1", "Appendix B1", "Appendix C1", "Appendix F1"}

with open("data/chunks.jsonl", encoding="utf-8") as f:
    cards = [json.loads(line) for line in f]

# matches pairs like "Energy Store (ES)" or "Lap Time Classified Session (LTCS)"
ABBREV = re.compile(r"\b([A-Z][A-Za-z]+(?:[ -][A-Z][A-Za-z]+){0,5}) \(([A-Z][A-Z0-9-]{1,9})\)")

pairs = Counter()
for c in cards:
    for full, short in ABBREV.findall(c["text"]):
        pairs[(short, full)] += 1

defs = [c for c in cards
        if c["rule"] in DEFINITION_APPENDICES or "DEFINITION" in (c["context"] + " " + c["title"]).upper()]

with open("data/rulebook_terms.txt", "w", encoding="utf-8") as out:
    out.write("=== ABBREVIATIONS ===\n")
    for (short, full), n in sorted(pairs.items()):
        out.write(f"{short} = {full}  ({n}x)\n")
    out.write(f"\n=== DEFINITION CARDS ({len(defs)}) ===\n")
    for c in defs:
        out.write(f"\n[{c['rule']}] {c['context']}\n{c['text']}\n")

print(f"{len(pairs)} abbreviations, {len(defs)} definition cards -> data/rulebook_terms.txt")