import json


def load(path):
    with open(path) as f:
        return json.load(f)


def run_eval(model, dataset):
    """Run every golden case; return per-case results."""
    results = []
    for case in dataset["cases"]:
        out = model.classify(case["input"])
        results.append({
            "id": case["id"],
            "difficulty": case.get("difficulty", "normal"),
            "expected": case["expected"],
            "got": out["category"],
            "pass": out["category"] == case["expected"],
        })
    return results


def accuracy(results):
    return sum(r["pass"] for r in results) / len(results) if results else 0.0


def per_category(results):
    cats = {}
    for r in results:
        c = cats.setdefault(r["expected"], [0, 0])
        c[1] += 1
        c[0] += r["pass"]
    return {k: v[0] / v[1] for k, v in cats.items()}
