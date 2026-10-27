"""Render scoreboard.json into a static HTML page for GitHub Pages.

Usage: python -I tools/render_scoreboard.py SCOREBOARD_JSON OUT_DIR
Validates the scoreboard against schema/scoreboard.schema.json first; exits non-zero if it does not validate.
"""
import html
import json
import os
import sys

import jsonschema

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_URL = "https://github.com/braxtonmensah/silicyte-grader-wargame"


def rows(entries):
    out = []
    for e in sorted(entries, key=lambda x: (x["utc"], x["level"])):
        sgx = html.escape(e.get("sgx_id", ""))
        out.append(
            "<tr>"
            f"<td><a href=\"https://github.com/{html.escape(e['handle'])}\">@{html.escape(e['handle'])}</a></td>"
            f"<td>{html.escape(e['level'])}</td><td>{html.escape(e['kind'])}{(' ' + sgx) if sgx else ''}</td>"
            f"<td><a href=\"{REPO_URL}/pull/{int(e['pr'])}\">#{int(e['pr'])}</a></td>"
            f"<td><a href=\"{html.escape(e['run_url'])}\">run</a></td>"
            f"<td>{html.escape(e['utc'])}</td></tr>")
    return "\n".join(out)


def table(entries, empty_text):
    if not entries:
        return f"<p class=\"empty\">{empty_text}</p>"
    return ("<table><thead><tr><th>Handle</th><th>Level</th><th>Kind</th><th>PR</th><th>CI run</th><th>UTC</th></tr>"
            f"</thead><tbody>\n{rows(entries)}\n</tbody></table>")


def render(board):
    players = [e for e in board["entries"] if not e["maintainer_test"]]
    tests = [e for e in board["entries"] if e["maintainer_test"]]
    handles = sorted({e["handle"].lower() for e in players})
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Grader Wargame Scoreboard</title>
<style>
:root {{ --bg:#fbfbf9; --fg:#1b1b1a; --muted:#5e5e5a; --line:#dcdcd6; --link:#1f5fbf; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#141413; --fg:#ececea; --muted:#a3a39e; --line:#34342f; --link:#8ab4ff; }} }}
body {{ background:var(--bg); color:var(--fg); font:16px/1.5 system-ui, sans-serif; margin:0; padding:24px 16px; }}
main {{ max-width:880px; margin:0 auto; }} a {{ color:var(--link); }} .muted, .empty {{ color:var(--muted); }}
table {{ width:100%; border-collapse:collapse; font-size:14px; display:block; overflow-x:auto; }}
th, td {{ text-align:left; padding:6px 10px; border-bottom:1px solid var(--line); white-space:nowrap; }}
</style></head><body><main>
<h1>Grader Wargame scoreboard</h1>
<p>Silicyte's graders, attackable, with CI-verified results. Every row below was written by CI
(<code>record.yml</code>) from a pull request's verdict, and links the PR and the Actions run that verified it.
Rules and levels: <a href="{REPO_URL}">{REPO_URL.replace('https://', '')}</a>.</p>
<p><strong>Players with a verified level:</strong> {len(handles)}</p>
<h2>Verified results</h2>
{table(players, "No verified results yet. Open a pull request to add one.")}
<h2>Maintainer CI self-tests</h2>
<p class="muted">Rows from the repository owner's own test pull requests. They show the pipeline works and are not
counted as players.</p>
{table(tests, "None.")}
<p class="muted">Built by Silicyte (silicyte.com) with AI assistance. Source data: scoreboard.json in the repository.</p>
</main></body></html>
"""


def main():
    src, out_dir = sys.argv[1], sys.argv[2]
    board = json.load(open(src, encoding="utf-8"))
    schema = json.load(open(os.path.join(ROOT, "schema", "scoreboard.schema.json"), encoding="utf-8"))
    jsonschema.validate(board, schema)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(board))
    print(f"rendered {len(board['entries'])} entries to {out_dir}/index.html")


if __name__ == "__main__":
    main()
