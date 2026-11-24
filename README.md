# LLM Regression Guard

CI-style regression check for an LLM feature. When a prompt or model changes, it runs a hand-labelled golden set, diffs against the baseline, flags regressions, and can alert Slack.

The feature under test is a support-email classifier (billing / technical / account / general).

## What it does
- Prompts are versioned JSON files in `prompts/`.
- `data/golden.json`: 38 hand-written synthetic cases (32 normal, 6 deliberately tricky), labels set by hand, not by an LLM.
- Scores exact-category match per case, per category, and overall.
- Compares candidate vs baseline: accuracy delta, per-category delta, cases that flipped to fail (regressions) and to pass (improvements).
- Thresholds: warning above a 3-point accuracy drop, critical above 8 (configurable in `compare()`).
- HTML report, optional Slack webhook (`SLACK_WEBHOOK_URL`), exit code 0/1/2 for CI gating.

## Honest scope
- The default backend is a deterministic keyword model driven by the prompt file, so the project runs offline with no API key. It is a stand-in to exercise the pipeline, not an LLM benchmark. `--backend openai` calls a real model if `OPENAI_API_KEY` is set (not run in CI, untested against the live API).
- The golden set is small and synthetic. The numbers below only show the pipeline works.

## Measured on the included prompts (rule backend)
| baseline -> candidate | accuracy | status |
|---|---|---|
| v1 -> v1 | 89.5% -> 89.5% | ok |
| v1 -> v2_bad | 89.5% -> 65.8%, 9 regressions | critical (exit 2) |
| v1 -> v2_good | 89.5% -> 97.4% | ok |

## Run
    python -m unittest discover -s tests      # 7 tests
    python -m rgd.cli prompts/v1.json prompts/v2_bad.json --html report.html

Standard library only, Python 3.10+.

## Demo and try it
- **Live app, no install:** https://pavan-llm-regression-guard.streamlit.app (free hosting, may take a few seconds to wake up)
- Demo video with voiceover (45 s): [demo/demo.mp4](demo/demo.mp4)
- Run the Streamlit app yourself on any machine with Python 3.10+:

      git clone https://github.com/Pavanteja0/llm-regression-guard
      cd llm-regression-guard
      pip install -r requirements.txt
      streamlit run app.py
