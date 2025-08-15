from pathlib import Path
import json

def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def write_md(path: Path, report: dict) -> None:
    lines = ["# Chart Analysis\n"]

    lines.append("## Chart Summary")
    for b in report.get("summary", []) or []:
        lines.append(f"- {b}")
    lines.append("")

    lines.append("## Key Observations")
    for b in report.get("observations", []) or []:
        lines.append(f"- {b}")
    lines.append("")

    lines.append("## Possible Improvements")
    for b in report.get("improvements", []) or []:
        lines.append(f"- {b}")
    lines.append("")

    if report.get("ocr_preview"):
        lines.append("## OCR Preview (snippets)")
        for t in report["ocr_preview"]:
            lines.append(f"- `{t}`")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
