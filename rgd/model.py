"""Model backends for the feature under test: classify a support email.

`RuleModel` is a deterministic offline stand-in whose behaviour is driven by the
keyword lists inside a prompt config. Changing the prompt file changes behaviour,
which is what the regression check needs. `OpenAIModel` calls a real API when
OPENAI_API_KEY is set (not used in CI).
"""
import json
import os
import urllib.request

CATEGORIES = ["billing", "technical", "account", "general"]


class RuleModel:
    def __init__(self, prompt):
        self.prompt = prompt

    def classify(self, text):
        t = text.lower()
        best, best_score = prompt_default(self.prompt), 0
        for cat in CATEGORIES:
            kws = self.prompt["keywords"].get(cat, [])
            score = sum(1 for k in kws if k in t)
            if score > best_score:
                best, best_score = cat, score
        return {"category": best, "summary": text.strip().split(".")[0][:100]}


def prompt_default(prompt):
    return prompt.get("default", "general")


class OpenAIModel:
    def __init__(self, prompt, model="gpt-4o-mini"):
        self.prompt, self.model = prompt, model
        self.key = os.environ["OPENAI_API_KEY"]

    def classify(self, text):
        body = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": self.prompt["system"]},
                {"role": "user", "content": text},
            ],
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Authorization": "Bearer " + self.key, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            out = json.load(r)
        data = json.loads(out["choices"][0]["message"]["content"])
        if data.get("category") not in CATEGORIES:
            data["category"] = "general"
        return data


def make_model(prompt, backend="rule"):
    return OpenAIModel(prompt) if backend == "openai" else RuleModel(prompt)
