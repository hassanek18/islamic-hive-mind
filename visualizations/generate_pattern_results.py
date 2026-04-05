"""Generate pattern verification results dashboard.

Shows all tested patterns with pass/fail status.
"""

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'hive-mind.db')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'pattern-results.html')


def generate(db_path=DB_PATH, output_path=OUTPUT_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
        SELECT name, category, description, claim, method, result,
               verified, significance, data, discovered_at
        FROM patterns ORDER BY category, name
    """)
    patterns = c.fetchall()

    c.execute("""
        SELECT analysis_type, interesting_findings, run_at
        FROM analysis_runs ORDER BY run_at DESC
    """)
    runs = c.fetchall()

    conn.close()

    pattern_rows = ""
    for p in patterns:
        name, cat, desc, claim, method, result, verified, sig, data_json, ts = p
        icon = "&#10004;" if verified else "&#10008;"
        color = "#4ecdc4" if verified else "#ff6b6b"
        sig_badge = f'<span style="color:{color}">{sig}</span>'

        # Parse data for details
        details = ""
        try:
            d = json.loads(data_json) if data_json else {}
            if 'actual' in d:
                details = f"Expected: {d.get('expected')}, Actual: {d.get('actual')}"
            elif 'counts' in d:
                details = ', '.join(f"{k}: {v}" for k, v in d['counts'].items())
        except Exception:
            details = str(result)[:100] if result else ""

        pattern_rows += f"""
        <tr>
            <td style="color:{color};font-size:18px;text-align:center">{icon}</td>
            <td>{name}</td>
            <td><code>{cat}</code></td>
            <td>{details}</td>
            <td>{sig_badge}</td>
        </tr>"""

    run_rows = ""
    for r in runs:
        run_rows += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>"

    confirmed = sum(1 for p in patterns if p[6])
    total = len(patterns)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Pattern Verification Results</title>
<style>
body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }}
h1 {{ text-align: center; color: #e0d68a; }}
h2 {{ color: #e0d68a; margin-top: 40px; }}
.summary {{ text-align: center; font-size: 24px; margin: 20px 0; }}
.confirmed {{ color: #4ecdc4; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
th {{ background: #16213e; color: #e0d68a; padding: 10px; text-align: left; }}
td {{ padding: 8px 10px; border-bottom: 1px solid #2a2a4a; }}
tr:hover {{ background: #16213e; }}
code {{ background: #2a2a4a; padding: 2px 6px; border-radius: 3px; font-size: 12px; }}
</style>
</head>
<body>
<h1>Pattern Verification Results</h1>
<div class="summary">
    <span class="confirmed">{confirmed}</span> / {total} patterns confirmed
</div>

<h2>Verified Patterns</h2>
<table>
    <tr><th></th><th>Pattern</th><th>Category</th><th>Details</th><th>Status</th></tr>
    {pattern_rows}
</table>

<h2>Analysis Runs</h2>
<table>
    <tr><th>Type</th><th>Findings</th><th>Date</th></tr>
    {run_rows}
</table>
</body>
</html>"""

    output_path = os.path.abspath(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  Generated: {output_path}")
    print(f"  Patterns: {confirmed}/{total} confirmed")


if __name__ == '__main__':
    print("Generating pattern results dashboard...")
    generate()
