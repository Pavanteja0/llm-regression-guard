"""Usage: python -m rgd.cli prompts/v1.json prompts/v2.json [--backend rule] [--html out.html]

Exit code 0 = ok, 1 = warning, 2 = critical, so CI can gate on it.
"""
import argparse
import json
import os
import sys
import urllib.request

from .compare import compare
from .evalrun import load, run_eval
from .model import make_model
from .report import render_html, slack_payload


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("baseline")
    p.add_argument("candidate")
    p.add_argument("--data", default="data/golden.json")
    p.add_argument("--backend", default="rule")
    p.add_argument("--html")
    a = p.parse_args(argv)
    data = load(a.data)
    base = run_eval(make_model(load(a.baseline), a.backend), data)
    new = run_eval(make_model(load(a.candidate), a.backend), data)
    diff = compare(base, new)
    print(json.dumps(diff, indent=2))
    if a.html:
        with open(a.html, "w") as f:
            f.write(render_html(diff, a.baseline, a.candidate))
    hook = os.environ.get("SLACK_WEBHOOK_URL")
    if hook and diff["status"] != "ok":
        req = urllib.request.Request(hook, data=json.dumps(slack_payload(diff, a.baseline, a.candidate)).encode(),
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    return {"ok": 0, "warning": 1, "critical": 2}[diff["status"]]


if __name__ == "__main__":
    sys.exit(main())
