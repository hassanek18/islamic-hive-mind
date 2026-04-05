"""Generate surah statistics dashboard with bar charts.

Shows verse count, word count, and letter count per surah using Chart.js.
"""

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'hive-mind.db')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'surah-dashboard.html')


def generate(db_path=DB_PATH, output_path=OUTPUT_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
        SELECT id, name_english, name_transliteration, revelation_type,
               verse_count, word_count, letter_count
        FROM surahs ORDER BY id
    """)
    surahs = c.fetchall()
    conn.close()

    labels = [f"{s[0]}. {s[2]}" for s in surahs]
    verses = [s[4] or 0 for s in surahs]
    words = [s[5] or 0 for s in surahs]
    letters = [s[6] or 0 for s in surahs]
    colors = ['#4ecdc4' if s[3] == 'meccan' else '#ff6b6b' for s in surahs]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Surah Statistics Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }}
h1 {{ text-align: center; color: #e0d68a; }}
.subtitle {{ text-align: center; color: #888; margin-bottom: 10px; }}
.legend {{ text-align: center; margin: 10px 0 20px; }}
.legend span {{ margin: 0 15px; }}
.meccan {{ color: #4ecdc4; }}
.medinan {{ color: #ff6b6b; }}
canvas {{ background: #16213e; border-radius: 8px; margin-bottom: 30px; }}
.chart-container {{ max-width: 1400px; margin: 0 auto; }}
</style>
</head>
<body>
<h1>Surah Statistics Dashboard</h1>
<p class="subtitle">All 114 Surahs of the Quran</p>
<div class="legend">
    <span class="meccan">&#9632; Meccan (86)</span>
    <span class="medinan">&#9632; Medinan (28)</span>
</div>
<div class="chart-container">
    <canvas id="versesChart" height="200"></canvas>
    <canvas id="wordsChart" height="200"></canvas>
    <canvas id="lettersChart" height="200"></canvas>
</div>
<script>
const labels = {json.dumps(labels)};
const verses = {json.dumps(verses)};
const words = {json.dumps(words)};
const letters = {json.dumps(letters)};
const colors = {json.dumps(colors)};

const chartOpts = {{
    responsive: true,
    plugins: {{
        legend: {{ display: false }},
    }},
    scales: {{
        x: {{ ticks: {{ display: false }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
        y: {{ grid: {{ color: 'rgba(255,255,255,0.1)' }}, ticks: {{ color: '#aaa' }} }}
    }}
}};

function makeChart(id, label, data) {{
    new Chart(document.getElementById(id), {{
        type: 'bar',
        data: {{
            labels: labels,
            datasets: [{{
                label: label,
                data: data,
                backgroundColor: colors,
                borderWidth: 0,
            }}]
        }},
        options: {{ ...chartOpts, plugins: {{ ...chartOpts.plugins, title: {{ display: true, text: label, color: '#e0d68a', font: {{ size: 16 }} }} }} }}
    }});
}}

makeChart('versesChart', 'Verse Count per Surah', verses);
makeChart('wordsChart', 'Word Count per Surah', words);
makeChart('lettersChart', 'Letter Count per Surah', letters);
</script>
</body>
</html>"""

    output_path = os.path.abspath(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  Generated: {output_path}")


if __name__ == '__main__':
    print("Generating surah dashboard...")
    generate()
