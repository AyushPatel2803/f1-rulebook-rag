# Findings (for the README)

- The fixes based on my own data worked. The fixes based only on other people's research didn't.
  - Worked: dedupe, top 8, gate off (each came from diagnose output)
  - Undone: cross-encoder reranker (fixed 4, broke 4), bge query label (no gain, shifted every score 3-6 points)
- The AI gives different answers to the same question, even at temperature 0, so ±2 questions between runs is noise.
- The prompt alone couldn't stop the jailbreak (#48); an output guard in code did.
- Similarity scores are bunched together (51-73%), so a fixed 65% gate blocked real questions.
- Turning the 65% gate off fixed #4 and #29, and the AI still refused all 3 tricks the gate used to block. The gate only added false refusals.