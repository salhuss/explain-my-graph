import typer
from pathlib import Path
from .ocr import ocr_extract
from .analyze import analyze_chart
from .export import write_md, write_json

app = typer.Typer(help="Explain My Graph CLI")

@app.command()
def main(
    image: str = typer.Argument(..., help="Path to chart image (png/jpg)"),
    out: str = typer.Option("out", help="Output directory"),
):
    """
    v0.1:
    - OCR the chart to extract text
    - Run LLM (or fallback) to produce Summary/Observations/Improvements
    - Export to report.md + report.json
    """
    out_p = Path(out); out_p.mkdir(parents=True, exist_ok=True)

    typer.echo("🖼️ Reading & OCR…")
    ocr = ocr_extract(image)

    typer.echo("🧠 Analyzing…")
    report = analyze_chart(image_path=image, ocr=ocr)

    typer.echo("📝 Exporting…")
    write_json(out_p / "report.json", report)
    write_md(out_p / "report.md", report)

    typer.echo(f"✅ Done → {out_p.resolve()}")
    for f in ["report.md", "report.json"]:
        typer.echo(f"   - {f}")

if __name__ == "__main__":
    app()
