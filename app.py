import json
import os

import streamlit as st

from rgd.compare import compare
from rgd.evalrun import load, run_eval
from rgd.model import RuleModel

ROOT = os.path.dirname(__file__)
st.set_page_config(page_title="LLM Regression Guard", layout="wide")
st.title("LLM Regression Guard")
st.caption("Compare a candidate prompt against a baseline on a hand-labelled golden set (38 synthetic cases, offline rule model).")

names = sorted(f for f in os.listdir(os.path.join(ROOT, "prompts")) if f.endswith(".json"))
c1, c2 = st.columns(2)
base_name = c1.selectbox("Baseline prompt", names, index=names.index("v1.json"))
new_name = c2.selectbox("Candidate prompt", names, index=names.index("v2_bad.json"))
warn = st.slider("Warning threshold (accuracy drop)", 0.0, 0.2, 0.03, 0.01)
crit = st.slider("Critical threshold (accuracy drop)", 0.0, 0.3, 0.08, 0.01)

if st.button("Run regression check", type="primary"):
    data = load(os.path.join(ROOT, "data", "golden.json"))
    ld = lambda n: load(os.path.join(ROOT, "prompts", n))
    base = run_eval(RuleModel(ld(base_name)), data)
    new = run_eval(RuleModel(ld(new_name)), data)
    d = compare(base, new, warn, crit)
    msg = "Accuracy %.1f%% -> %.1f%% (%+.1f points)" % (d["base_accuracy"] * 100, d["new_accuracy"] * 100, d["delta"] * 100)
    {"ok": st.success, "warning": st.warning, "critical": st.error}[d["status"]](
        "%s: %s" % (d["status"].upper(), msg))
    m1, m2, m3 = st.columns(3)
    m1.metric("Baseline accuracy", "%.1f%%" % (d["base_accuracy"] * 100))
    m2.metric("Candidate accuracy", "%.1f%%" % (d["new_accuracy"] * 100), "%+.1f%%" % (d["delta"] * 100))
    m3.metric("Regressions", len(d["regressions"]))
    st.subheader("Per-category change")
    st.bar_chart({k: v * 100 for k, v in d["category_delta"].items()})
    cases = {c["id"]: c for c in data["cases"]}
    bm = {r["id"]: r for r in base}
    nm = {r["id"]: r for r in new}
    st.subheader("Cases that flipped to fail")
    st.table([{"id": i, "email": cases[i]["input"], "expected": cases[i]["expected"],
               "baseline": bm[i]["got"], "candidate": nm[i]["got"]} for i in d["regressions"]] or [{"result": "none"}])
    st.subheader("Cases that flipped to pass")
    st.table([{"id": i, "email": cases[i]["input"], "expected": cases[i]["expected"],
               "baseline": bm[i]["got"], "candidate": nm[i]["got"]} for i in d["improvements"]] or [{"result": "none"}])
