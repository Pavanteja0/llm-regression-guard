from .evalrun import accuracy, per_category

WARN = 0.03
CRIT = 0.08


def compare(base, new, warn=WARN, crit=CRIT):
    """Diff two eval runs. Delta is new accuracy minus baseline accuracy."""
    b = {r["id"]: r for r in base}
    n = {r["id"]: r for r in new}
    regressions = sorted(i for i in b if i in n and b[i]["pass"] and not n[i]["pass"])
    improvements = sorted(i for i in b if i in n and not b[i]["pass"] and n[i]["pass"])
    delta = accuracy(new) - accuracy(base)
    drop = -delta
    if drop > crit:
        status = "critical"
    elif drop > warn:
        status = "warning"
    else:
        status = "ok"
    bc, nc = per_category(base), per_category(new)
    cat_delta = {c: round(nc.get(c, 0) - bc.get(c, 0), 4) for c in sorted(set(bc) | set(nc))}
    return {
        "base_accuracy": round(accuracy(base), 4),
        "new_accuracy": round(accuracy(new), 4),
        "delta": round(delta, 4),
        "status": status,
        "regressions": regressions,
        "improvements": improvements,
        "category_delta": cat_delta,
    }
