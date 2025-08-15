# explain_graph/analyze.py
from __future__ import annotations
from typing import Dict, Any
import os
import json

PROMPT_SYS = "You analyze chart screenshots. Be precise and concise."

PROMPT_USER_TMPL = """You are given:
- OCR text snippets from a chart image
- A heuristic guess of the chart type and basic features

Chart guess:
type: {chart_type}
features: {features_json}

OCR text snippets:
{ocr_texts}

Tasks:
1) Chart Summary (2–4 bullets): what the chart is about and its main trend.
2) Key Observations (3–6 bullets): notable increases/decreases, inflection points, comparisons.
3) Possible Improvements (2–4 bullets): missing labels, better scales, more context.
4) If the guessed type seems wrong, briefly say so and state what it likely is.

Constraints:
- If OCR is weak, be explicit about uncertainty.
- Do not hallucinate exact numbers; qualify estimates.
Return strict JSON with keys: summary, observations, improvements (arrays of bullets) and optional field 'type_feedback'.
"""

def _fallback_report(ocr: Dict[str, Any], chart_type: str, features: Dict[str, Any]) -> Dict[str, Any]:
    texts = ocr.get("texts", [])
    return {
        "summary": [
            "(Placeholder) Provide OPENAI_API_KEY for LLM-based analysis.",
            f"OCR detected ~{len(texts)} text snippets.",
            f"Heuristic chart type: {chart_type or 'unknown'}",
        ],
        "observations": [
            f"Rect bars: {features.get('bar_like_rectangles')}, "
            f"Line segments: {features.get('line_segments')}, "
            f"Blobs: {features.get('point_like_blobs')}.",
            "Trends/insights pending LLM analysis."
        ],
        "improvements": [
            "Ensure chart title and axis labels are readable.",
            "Use high-contrast colors for lines/bars and labels."
        ],
        "ocr_preview": texts[:12],
        "type_feedback": None,
    }

def analyze_chart(image_path: str, ocr: Dict[str, Any], chart_type: str, features: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    ocr_texts = "\n".join(ocr.get("texts", [])[:50]) or "(no OCR text)"
    feat_json = json.dumps(features, ensure_ascii=False)

    if not api_key:
        return _fallback_report(ocr, chart_type, features)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": PROMPT_SYS},
                {"role": "user", "content": PROMPT_USER_TMPL.format(
                    chart_type=chart_type or "unknown",
                    features_json=feat_json,
                    ocr_texts=ocr_texts)}
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        msg = resp.choices[0].message
        parsed = getattr(msg, "parsed", None)
        out = parsed if parsed is not None else json.loads(msg.content)
        out["ocr_preview"] = ocr.get("texts", [])[:12]
        if "type_feedback" not in out:
            out["type_feedback"] = None
        return out
    except Exception as e:
        fb = _fallback_report(ocr, chart_type, features)
        fb["summary"][0] = "(LLM error) Could not generate analysis."
        fb["summary"].append(f"Reason: {type(e).__name__}")
        return fb
