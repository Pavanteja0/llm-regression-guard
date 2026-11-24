import html


def render_html(diff, base_name, new_name):
    rows = "".join(
        "<tr><td>%s</td><td>%+.1f%%</td></tr>" % (html.escape(c), d * 100)
        for c, d in diff["category_delta"].items()
    )
    reg = ", ".join(map(html.escape, diff["regressions"])) or "none"
    imp = ", ".join(map(html.escape, diff["improvements"])) or "none"
    return (
        "<html><body><h1>Regression report</h1>"
        "<p>Baseline <b>%s</b> vs candidate <b>%s</b></p>"
        "<p>Accuracy %.1f%% -> %.1f%% (%+.1f%%). Status: <b>%s</b></p>"
        "<p>Regressions: %s</p><p>Improvements: %s</p>"
        "<table border=1><tr><th>Category</th><th>Delta</th></tr>%s</table></body></html>"
        % (html.escape(base_name), html.escape(new_name), diff["base_accuracy"] * 100,
           diff["new_accuracy"] * 100, diff["delta"] * 100, diff["status"], reg, imp, rows)
    )


def slack_payload(diff, base_name, new_name):
    emoji = {"ok": "white_check_mark", "warning": "warning", "critical": "rotating_light"}[diff["status"]]
    return {"text": ":%s: %s -> %s accuracy %.1f%% -> %.1f%%, %d regressions" % (
        emoji, base_name, new_name, diff["base_accuracy"] * 100, diff["new_accuracy"] * 100,
        len(diff["regressions"]))}
