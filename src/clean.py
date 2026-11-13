from pathlib import Path
from collections import Counter
import json
import re

in_path = Path("data/pages.jsonl")
out_path = Path("data/pages_clean.jsonl")

# 1. Read every page card back in
pages = []
with open(in_path, encoding="utf-8") as f:
    for line in f:
        pages.append(json.loads(line))

# 2. Count how many pages each line appears on (per rulebook)
line_counts = Counter()
pages_per_doc = Counter()
for p in pages:
    pages_per_doc[p["doc"]] += 1
    for line in set(p["text"].splitlines()):
        line_counts[(p["doc"], line.strip())] += 1

# 3. Rebuild each page without the junk
removed = set()
with open(out_path, "w", encoding="utf-8") as out:
    for p in pages:
        keep = []
        label = None
        for line in p["text"].splitlines():
            s = line.strip()
            is_list_marker = re.fullmatch(r"[a-z]{1,4}\.", s)
            if s and not is_list_marker and line_counts[(p["doc"], s)] > pages_per_doc[p["doc"]] / 2:
                removed.add(s)
                continue
            if label is None and re.fullmatch(r"[A-F]\d+", s):
                label = s
                continue
            keep.append(line)
        p["label"] = label
        p["text"] = "\n".join(keep).strip()
        out.write(json.dumps(p, ensure_ascii=False) + "\n")

print("Saved clean pages to", out_path)
print("Removed these repeating lines:")
for s in sorted(removed):
    print("   ", repr(s))