from pathlib import Path
import json
import pymupdf

pdf_files = sorted(Path("data/raw").glob("*.pdf"))
out_path = Path("data/pages.jsonl")

total_pages = 0
with open(out_path, "w", encoding="utf-8") as out:
    for pdf in pdf_files:
        parts = pdf.stem.split(" - ")
        section = parts[1]    # e.g. "Section B [Sporting]"
        issue = parts[2]      # e.g. "Iss 09"

        doc = pymupdf.open(pdf)
        for page_num, page in enumerate(doc, start=1):
            record = {
                "doc": section,
                "issue": issue,
                "page": page_num,
                "text": page.get_text(),
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            total_pages += 1

        print(" -", section, "|", issue, "|", len(doc), "pages")

print("Saved", total_pages, "pages to", out_path)