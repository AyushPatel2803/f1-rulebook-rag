"""Split the cleaned FIA regulation pages into one chunk per rule."""

import json
import re

pages = []
with open("data/pages_clean.jsonl", encoding="utf-8") as f:
    for line in f:
        pages.append(json.loads(line))

# FIA prints the rule number on its own line and the title on the line after it
rule_number = re.compile(r"^[A-F]\d+(?:\.\d+)+$")
article = re.compile(r"^ARTICLE\s+([A-F]\d+):\s*(.*)$")
# real appendix headings are uppercase; lowercase "Appendix" is just a mention in a sentence
appendix = re.compile(r"^APPENDIX\s+([A-F]\d+):\s*(.*)$")

chunks = []
current = None

for p in pages:
    if current and current["doc"] != p["doc"]:
        chunks.append(current)
        current = None

    page_lines = p["text"].splitlines()
    for i, line in enumerate(page_lines):
        s = line.strip()
        rule = None
        title = ""

        if rule_number.match(s):
            rule = s
            if i + 1 < len(page_lines):
                nxt = page_lines[i + 1].strip()
                # titles are short and never end with a period
                if len(nxt) <= 70 and not nxt.endswith("."):
                    title = nxt
        elif article.match(s):
            a = article.match(s)
            rule = a.group(1)
            title = a.group(2)
        elif appendix.match(s):
            a = appendix.match(s)
            rule = "Appendix " + a.group(1)
            title = a.group(2)

        if rule:
            if current:
                chunks.append(current)
            current = {
                "doc": p["doc"],
                "issue": p["issue"],
                "rule": rule,
                "title": title,
                "lines": [],
            }
        if current is None:
            continue
        current["lines"].append((p["label"], line.rstrip()))

if current:
    chunks.append(current)

titles = {}
for c in chunks:
    if c["title"] and c["rule"] not in titles:
        titles[c["rule"]] = c["title"]


def breadcrumb(rule):
    """B1.1.1 -> 'B1 <title> > B1.1 <title> > B1.1.1'"""
    parts = rule.split(".")
    trail = []
    for n in range(1, len(parts) + 1):
        r = ".".join(parts[:n])
        trail.append((r + " " + titles.get(r, "")).strip())
    return " > ".join(trail)


MIN_CHARS = 80    # below this it's a contents-page entry or an empty heading
MAX_CHARS = 2000  # keeps chunks within what the embedding model handles well

final = []
seen = {}
dropped = 0

for c in chunks:
    text = "\n".join(line for label, line in c["lines"]).strip()

    if len(text) < MIN_CHARS:
        dropped += 1
        continue

    parts = []
    cur_lines = []
    cur_len = 0
    for label, line in c["lines"]:
        if cur_len + len(line) > MAX_CHARS and cur_lines:
            parts.append(cur_lines)
            cur_lines = []
            cur_len = 0
        cur_lines.append((label, line))
        cur_len += len(line) + 1
    if cur_lines:
        parts.append(cur_lines)

    # the contents page and body can both produce the same rule number
    seen[c["rule"]] = seen.get(c["rule"], 0) + 1
    if seen[c["rule"]] == 1:
        base_id = c["rule"]
    else:
        base_id = f'{c["rule"]}-{seen[c["rule"]]}'

    for n, part in enumerate(parts, start=1):
        pages_in_part = []
        for label, line in part:
            if label and label not in pages_in_part:
                pages_in_part.append(label)

        final.append({
            "id": base_id if len(parts) == 1 else f"{base_id}#{n}",
            "doc": c["doc"],
            "issue": c["issue"],
            "rule": c["rule"],
            "title": c["title"],
            "context": breadcrumb(c["rule"]),
            "pages": pages_in_part,
            "text": "\n".join(line for label, line in part).strip(),
        })

with open("data/chunks.jsonl", "w", encoding="utf-8") as out:
    for ch in final:
        out.write(json.dumps(ch, ensure_ascii=False) + "\n")

sizes = [len(ch["text"]) for ch in final]
print("Raw rule chunks:   ", len(chunks))
print("Dropped as junk:   ", dropped)
print("Final chunks saved:", len(final))
print("Average size:", sum(sizes) // len(sizes), "chars | Biggest:", max(sizes), "chars")

for ch in final:
    if ch["rule"] == "B1.9.6":
        print()
        print(json.dumps(ch, ensure_ascii=False, indent=2)[:900])
        break

for c in chunks:
    if c["rule"] == "C18.6":
        labels = [label for label, line in c["lines"] if label]
        print()
        print("C18.6 runs from page", labels[0], "to", labels[-1])

appendix_chunks = [ch for ch in final if ch["rule"].startswith("Appendix")]
print("Appendix chunks:", len(appendix_chunks))