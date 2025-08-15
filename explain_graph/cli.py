# explain_graph/cli.py
import typer
from pathlib import Path
from .ocr import ocr_extract
from .analyze import analyze_chart
from .export import write_md, write_json
from .detect import detect_chart_type
from .visualize import draw_overlay

app = typer.Typer(help="Explain My Graph CLI")

@app.command()
def main(
    image: str = typer.Argument(..., help="Path to chart image (png/jpg)"),
    out: str = typer.Option("out", help="Output directory"),
    debug_image: bool = typer.Option(True, "--debug-image/--no-debug-image",
                                     help="Save overlay highlighting detected bars/lines/points"),
):
    """
    v0.3:
    - OCR the chart (texts)
    - Heuristically detect chart type & simple features
    - (Optional) Save overlay image with detected elements
    - Run LLM (or fallback) to produce Summary/Observations/Improvements (+type_feedback)
    - Export report.md + report.json
    """
    out_p = Path(out); out_p.mkdir(parents=True, exist_ok=True)

    typer.echo("🖼️ Reading & OCR…")
    ocr = ocr_extract(image)

    typer.echo("🔎 Detecting chart type…")
    guess = detect_chart_type(image)
    typer.echo(f"   → type={guess.chart_type} | features={guess.features}")

    if debug_image:
        typer.echo("🎨 Drawing overlay…")
        overlay_path = draw_overlay(image, str(out_p / "overlay.png"))
        typer.echo(f"   → overlay: {overlay_path}")

    typer.echo("🧠 Analyzing…")
    report = analyze_chart(image_path=image, ocr=ocr, chart_type=guess.chart_type, features=guess.features)
    report["detected_type"] = guess.chart_type
    report["detected_features"] = guess.features
    report["overlay_image"] = "overlay.png" if debug_image else None

    typer.echo("📝 Exporting…")
    write_json(out_p / "report.json", report)
    write_md(out_p / "report.md", report)

    typer.echo(f"✅ Done → {out_p.resolve()}")
    emitted = ["report.md", "report.json", "overlay.png" if debug_image else None]
    for f in filter(None, emitted):
        typer.echo(f"   - {f}")

if __name__ == "__main__":
    app()
