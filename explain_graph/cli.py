# explain_graph/cli.py
import typer
from pathlib import Path
from .ocr import ocr_extract
from .analyze import analyze_chart
from .export import write_md, write_json
from .detect import detect_chart_type

app = typer.Typer(help="Explain My Graph CLI")

@app.command()
def main(
    image: str = typer.Argument(..., help="Path to chart image (png/jpg)"),
    out: str = typer.Option("out", help="Output directory"),
):
    """
    v0.2:
    - OCR the chart (texts)
    - Heuristically detect chart type & simple features
    - Run LLM (or fallback) to produce Summary/Observations/Improvements (+type_feedback)
    - Export report.md + report.json
    """
    out_p = Path(out); out_p.mkdir(parents=True, exist_ok=True)

    typer.echo("🖼️ Reading & OCR…")
    ocr = ocr_extract(image)

    typer.echo("🔎 Detecting chart type…")
    guess = detect_chart_type(image)
    typer.echo(f"   → type={guess.chart_type} | features={guess.features}")

    typer.echo("🧠 Analyzing…")
    report = analyze_chart(image_path=image, ocr=ocr, chart_type=guess.chart_type, features=guess.features)
    report["detected_type"] = guess.chart_type
    report["detected_features"] = guess.features

    typer.echo("📝 Exporting…")
    write_json(out_p / "report.json", report)
    write_md(out_p / "report.md", report)

    typer.echo(f"✅ Done → {out_p.resolve()}")
    for f in ["report.md", "report.json"]:
        typer.echo(f"   - {f}")

if __name__ == "__main__":
    app()
