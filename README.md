# explain-my-graph
Upload a chart image → AI explains the trends, key takeaways, and how to improve the analysis.

Give me a chart image (bar, line, scatter, etc.) and I’ll:
- Extract text (title, axes, legend) via OCR
- Summarize trends and key takeaways
- Suggest improvements or missing context

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m explain_graph.cli path/to/chart.png --out out/
