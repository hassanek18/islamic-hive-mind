"""Generate a letter frequency heatmap across all 114 surahs.

Produces an interactive HTML file using D3.js showing letter frequency
as a heatmap grid (surah x letter).
"""

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'hive-mind.db')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'letter-frequency-heatmap.html')


def generate(db_path=DB_PATH, output_path=OUTPUT_PATH):
    db_path = os.path.abspath(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get letter frequencies per surah
    c.execute("""
        SELECT surah_id, letter_arabic, COUNT(*) as freq
        FROM letters
        GROUP BY surah_id, letter_arabic
        ORDER BY surah_id, freq DESC
    """)
    rows = c.fetchall()

    # Get surah names
    c.execute("SELECT id, name_english, name_transliteration FROM surahs ORDER BY id")
    surahs = [{'id': r[0], 'name': r[1], 'translit': r[2]} for r in c.fetchall()]

    # Get unique letters ordered by frequency
    c.execute("""
        SELECT letter_arabic, COUNT(*) as total
        FROM letters
        GROUP BY letter_arabic
        ORDER BY total DESC
    """)
    letters = [r[0] for r in c.fetchall()]

    conn.close()

    # Build data matrix
    data = []
    for surah_id, letter, freq in rows:
        data.append({'surah': surah_id, 'letter': letter, 'freq': freq})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Quran Letter Frequency Heatmap</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }}
h1 {{ text-align: center; color: #e0d68a; }}
.subtitle {{ text-align: center; color: #888; margin-bottom: 20px; }}
#chart {{ overflow-x: auto; }}
.tooltip {{
    position: absolute; padding: 8px 12px; background: rgba(0,0,0,0.85);
    color: #fff; border-radius: 4px; font-size: 13px; pointer-events: none;
    border: 1px solid #e0d68a;
}}
.letter-label {{ font-size: 14px; font-family: 'Traditional Arabic', 'Amiri', serif; }}
</style>
</head>
<body>
<h1>Quran Letter Frequency Heatmap</h1>
<p class="subtitle">Frequency of each Arabic letter across all 114 surahs</p>
<div id="chart"></div>
<script>
const data = {json.dumps(data)};
const surahs = {json.dumps(surahs)};
const letters = {json.dumps(letters)};

const margin = {{top: 80, right: 30, bottom: 40, left: 60}};
const cellSize = 5;
const width = surahs.length * cellSize + margin.left + margin.right;
const height = letters.length * (cellSize + 2) + margin.top + margin.bottom;

const svg = d3.select("#chart").append("svg")
    .attr("width", width).attr("height", height);

const g = svg.append("g").attr("transform", `translate(${{margin.left}},${{margin.top}})`);

const maxFreq = d3.max(data, d => d.freq);
const color = d3.scaleSequential(d3.interpolateYlOrRd).domain([0, maxFreq * 0.3]);

const x = d3.scaleBand().domain(surahs.map(s => s.id)).range([0, surahs.length * cellSize]);
const y = d3.scaleBand().domain(letters).range([0, letters.length * (cellSize + 2)]);

// Tooltip
const tooltip = d3.select("body").append("div").attr("class", "tooltip").style("opacity", 0);

// Cells
g.selectAll("rect")
    .data(data)
    .join("rect")
    .attr("x", d => x(d.surah))
    .attr("y", d => y(d.letter))
    .attr("width", cellSize)
    .attr("height", cellSize)
    .attr("fill", d => color(d.freq))
    .on("mouseover", (event, d) => {{
        const s = surahs.find(s => s.id === d.surah);
        tooltip.transition().duration(100).style("opacity", 1);
        tooltip.html(`<strong>${{d.letter}}</strong> in Surah ${{d.surah}} (${{s ? s.translit : ''}})<br>Count: ${{d.freq}}`)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 28) + "px");
    }})
    .on("mouseout", () => tooltip.transition().duration(200).style("opacity", 0));

// Y axis (letters)
g.selectAll(".letter-label")
    .data(letters)
    .join("text")
    .attr("class", "letter-label")
    .attr("x", -8)
    .attr("y", d => y(d) + cellSize / 2 + 4)
    .attr("text-anchor", "end")
    .text(d => d);

// X axis labels (every 10th surah)
g.selectAll(".surah-label")
    .data(surahs.filter(s => s.id % 10 === 0))
    .join("text")
    .attr("x", d => x(d.id) + cellSize / 2)
    .attr("y", -5)
    .attr("text-anchor", "middle")
    .attr("font-size", "10px")
    .attr("fill", "#aaa")
    .text(d => d.id);
</script>
</body>
</html>"""

    output_path = os.path.abspath(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  Generated: {output_path}")
    print(f"  Data points: {len(data)}")


if __name__ == '__main__':
    print("Generating letter frequency heatmap...")
    generate()
