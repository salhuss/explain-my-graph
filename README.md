# Explain My Graph

Upload a chart image (bar, line, scatter, etc.) and get an AI-generated report that explains:
- The **main trend** and what the chart is about
- **Key observations** such as increases, decreases, and outliers
- **Possible improvements** for better clarity and analysis
- An **optional debug overlay image** highlighting detected bars, lines, and scatter points

---

## ✨ Features

- 🖼️ **Chart OCR** — Extracts text from the chart (titles, axis labels, legends) using EasyOCR
- 🧭 **Chart-type detection** — Heuristically identifies bar, line, scatter, or unknown
- 🧠 **AI analysis** — Uses LLM to summarize trends, insights, and suggestions (requires `OPENAI_API_KEY`; fallback provided)
- 🎨 **Debug overlay** — Saves `overlay.png` with:
  - Green rectangles = bars
  - Red lines = line segments
  - Blue circles = scatter points
- 📄 **Exports**:
  - `report.md` — Readable Markdown summary
  - `report.json` — Structured data including detected type, features, and OCR preview

---

## 📦 Installation

```bash
git clone https://github.com/<your-username>/explain-my-graph.git
cd explain-my-graph

python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

pip install -r requirements.txt
```

---

## 🔑 OpenAI API Key (optional)

If you want **real LLM analysis** (instead of the offline fallback):

```bash
export OPENAI_API_KEY=sk-...       # Mac/Linux
setx OPENAI_API_KEY "sk-..."       # Windows (PowerShell)
```

You can also set a specific model:

```bash
export OPENAI_MODEL=gpt-4o-mini
```

If no key is provided, you will still get OCR results, chart-type detection, and a placeholder analysis.

---

## 🚀 Usage

### Basic run (default overlay enabled)
```bash
python -m explain_graph.cli path/to/chart.png --out out/
```

### Disable debug overlay
```bash
python -m explain_graph.cli path/to/chart.png --out out/ --no-debug-image
```

---

## 📂 Output Example

Running on `examples/chart.png` produces:

```
out/
├── report.json          # Structured report (summary, observations, improvements, type_feedback, OCR preview)
├── report.md            # Human-readable Markdown report
└── overlay.png          # Debug overlay showing detected chart features (if enabled)
```

---

## 📝 Example `report.md`

```markdown
# Chart Analysis

## Chart Summary
- This bar chart shows quarterly sales from 2022 to 2024.
- Sales steadily increased, with a sharp jump in Q4 2023.

## Key Observations
- Largest increase occurred between Q3 and Q4 2023.
- Slight dip in Q2 2022.
- Labels and axis titles are clear and legible.

## Possible Improvements
- Add numerical values above each bar.
- Include a trend line for easier growth visualization.

## OCR Preview (snippets)
- `Q1 2022`
- `Q2 2022`
- `Sales`
- `Revenue`
```

---

## ⚙️ CLI Options

| Option               | Description |
|----------------------|-------------|
| `image`              | Path to the chart image file (png/jpg) |
| `--out`              | Output directory (default: `out`) |
| `--debug-image`      | Save overlay.png highlighting detected bars/lines/points (default: on) |
| `--no-debug-image`   | Skip generating the overlay image |

---

## 🛠 How It Works

1. **OCR Extraction** (`ocr.py`)  
   - Converts image to grayscale, applies thresholding, and runs EasyOCR.
2. **Chart-Type Detection** (`detect.py`)  
   - Uses OpenCV to count bars, line segments, and blobs to guess chart type.
3. **Overlay Visualization** (`visualize.py`)  
   - Draws detected features over the chart for inspection.
4. **LLM Analysis** (`analyze.py`)  
   - Merges OCR text + detected features into an AI prompt for summarization.
5. **Export** (`export.py`)  
   - Saves the report as Markdown and JSON.

---

## 🛣 Roadmap

- [ ] Data point extraction from charts
- [ ] Support for pie/donut charts
- [ ] Web UI for drag-and-drop chart analysis
- [ ] Multi-language OCR

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

