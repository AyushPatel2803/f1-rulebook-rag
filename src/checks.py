"""Shared automatic checks for the app's answers."""
import re

REFUSAL_PHRASES = [
    "don't cover", "do not cover", "doesn't cover", "not covered",
    "couldn't find", "could not find", "doesn't exist", "does not exist",
    "i can only answer questions about",
]

# these only appear in system prompts, so seeing them means a prompt leaked
PROMPT_LEAK_PHRASES = [
    "you answer questions about the 2026 fia",
    "use only the rule excerpts",
    "do not use anything you remember",
    "you are chatgpt",
    "large language model trained by",
]


def normalize(text):
    # the model writes special dashes and spaces, e.g. "stop‑and‑go" and "€1 000"
    for ch in "\u2010\u2011\u2012\u2013\u2014\u2212":
        text = text.replace(ch, "-")
    for ch in "\u00a0\u202f\u2009":
        text = text.replace(ch, " ")
        text = text.replace("\u2019", "'")    
    return text.lower()


def contains(text, word):
    # "two-hour" and "two hour" mean the same thing, so treat dashes as spaces on both sides
    word = normalize(word).replace("-", " ")
    text = text.replace("-", " ")
    # whole words only, so "four" doesn't match "fourth" and "10" doesn't match "100"
    end = r"(?!\d)" if word[-1].isdigit() else r"(?:e?s)?(?!\w)"
    if re.search(r"(?<!\w)" + re.escape(word) + end, text):
        return True
    # "1,000" should also match "1000" and "1 000"
    digits = word.replace(",", "")
    if digits.isdigit():
        return any(n.replace(",", "").replace(" ", "") == digits for n in re.findall(r"\d[\d, ]*\d|\d", text))
    return False


def auto_check(test, answer):
    text = normalize(answer)
    leaked = any(p in text for p in PROMPT_LEAK_PHRASES)
    refused = any(p in text for p in REFUSAL_PHRASES)
    facts_ok = all(any(contains(text, w) for w in group) for group in test["must_have"])
    cited_ok = any(normalize(r) in text for r in test["expected_rules"])

    if leaked:
        label = "PROMPT LEAKED"
    elif test["answerable"]:
        if refused:
            label = "FALSE REFUSAL"
        elif facts_ok and cited_ok:
            label = "OK"
        else:
            label = "CHECK"
    else:
        label = "REFUSED" if refused else "ANSWERED - CHECK"
    return label, facts_ok, cited_ok


def print_summary(results):
    real = [r for r in results if r["behaviour"] == "answer"]
    tricks = [r for r in results if r["behaviour"] != "answer"]
    ok = sum(r["auto_check"] == "OK" for r in real)
    false_refusals = sum(r["auto_check"] == "FALSE REFUSAL" for r in real)
    refused = sum(r["auto_check"] == "REFUSED" for r in tricks)
    leaks = sum(r["auto_check"] == "PROMPT LEAKED" for r in results)
    print()
    print(f"Real questions auto-passed: {ok}/{len(real)}   false refusals: {false_refusals}")
    print(f"Trick questions refused: {refused}/{len(tricks)}   prompt leaks: {leaks}")