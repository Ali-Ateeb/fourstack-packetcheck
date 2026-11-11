"""Offline classification of fictional referral handoff sentences."""

import argparse
from collections import Counter
from math import log
from pathlib import Path
import json
import re


FIELDS = {
    "callback": [
        "contact the booking desk using extension",
        "call the caregiver at the listed number",
        "reach scheduling by telephone",
        "callback phone is on the packet cover sheet",
    ],
    "visit_window": [
        "schedule the visit within the next week",
        "appointment window is the first week of June",
        "booking target is within five days",
        "follow-up visit is planned for next month",
    ],
    "records": [
        "supporting report is attached to this packet",
        "enclosed are the relevant visit notes",
        "the referral document and results accompany this form",
        "records included in the packet attachment list",
    ],
}
BACKGROUND = [
    "the clinic lobby is being painted",
    "the chart is stored securely",
    "the bus stop is across the street",
    "the assistant reviewed the queue",
    "the packet arrived in a blue folder",
]
STOP = set("a an are at by for in is it of on or the this to was with".split())
UNCERTAIN = re.compile(
    r"\b(?:no|not|never|missing|unknown|pending|awaiting|unconfirmed|"
    r"unavailable|uncertain|maybe|might|should|if|tbd|blank|optional|"
    r"will be|to be provided|call later|without)\b",
    re.IGNORECASE,
)


def tokens(text):
    return set(re.findall(r"[a-z]+", text.lower())) - STOP


def train():
    examples = {**FIELDS, "background": BACKGROUND}
    document_tokens = {label: [tokens(item) for item in items] for label, items in examples.items()}
    counts = {label: Counter(word for item in items for word in item)
              for label, items in document_tokens.items()}
    vocabulary = set().union(*(set(counter) for counter in counts.values()))
    return counts, vocabulary


COUNTS, VOCABULARY = train()


def classify(sentence):
    """Return a field only when two known words support a clear match."""
    words = tokens(sentence) & VOCABULARY
    if len(words) < 2 or UNCERTAIN.search(sentence) or "?" in sentence:
        return None
    scores = []
    for label, counter in COUNTS.items():
        total = counter.total() + len(VOCABULARY)
        score = sum(log((counter[word] + 1) / total) for word in words)
        scores.append((score, label))
    scores.sort(reverse=True)
    first, second = scores[:2]
    if first[1] == "background" or first[0] - second[0] < 0.9:
        return None
    return first[1]


def check(text):
    findings = {field: [] for field in FIELDS}
    sentences = re.split(r"\n|(?<=[.!?;])\s+", text)
    for sentence in sentences:
        sentence = sentence.strip()
        label = classify(sentence)
        if label:
            findings[label].append(sentence)
    return findings


def evaluate(cases):
    results = []
    true_positive = false_positive = false_negative = 0
    for case in cases:
        prediction = set(field for field, evidence in check(case["text"]).items() if evidence)
        expected = set(case["expected"])
        true_positive += len(prediction & expected)
        false_positive += len(prediction - expected)
        false_negative += len(expected - prediction)
        results.append({
            "case": case["id"], "expected": sorted(expected),
            "observed": sorted(prediction), "exact_match": expected == prediction,
        })
    return {
        "dataset": "Fictional cases held out from model training",
        "cases": len(cases),
        "exact_matches": sum(result["exact_match"] for result in results),
        "true_positive": true_positive, "false_positive": false_positive,
        "false_negative": false_negative, "results": results,
    }


def main():
    cases = json.loads(Path(__file__).with_name("fictional-cases.json").read_text(encoding="utf-8"))
    by_id = {case["id"]: case for case in cases}
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    demo = commands.add_parser("demo", help="Check one fictional packet")
    demo.add_argument("case", choices=by_id, nargs="?", default="all-fields")
    commands.add_parser("evaluate", help="Measure performance on all fictional cases")
    args = parser.parse_args()
    if args.mode == "evaluate":
        result = evaluate(cases)
    else:
        sample = by_id[args.case]
        result = {
            "input": sample["text"],
            "fields": {
                field: {"status": "Evidence found" if evidence else "Needs human review",
                        "evidence": evidence}
                for field, evidence in check(sample["text"]).items()
            },
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
