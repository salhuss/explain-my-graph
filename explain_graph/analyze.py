from __future__ import annotations
from typing import Dict, Any
import os

PROMPT_SYS = (
    "You analyze chart screenshots. Be precise and concise."
)

PROMPT_USER_TMPL = """You are given a chart image description (via OCR) and should write a short analysis.

OCR text snippets:
{ocr_texts}

Tasks:
1) Chart Summary (2–4 bullets): what the chart is about and its main trend.
2) Key Observations (3–6 bullets): notable increases/decreases, outliers, comparisons.
3) Possible Improvements (2–4 bullets): missing labels, better scales, more context.

Constraints:
- If the OCR is weak, be explicit about uncertainty.
- Do not hallucinate exact numbers; qualify estimates.
Return strict JSON with keys: summary, observations, improvements (each an array of bullets).
"""

def _fallback_report(ocr: Dict[str, Any]) -> Dict[str, Any]:
    texts = ocr.get("texts", [])
    return {
        "summary": [
            "(Placeholder) Provide OPENAI_API_KEY for LLM-based analysis.",
            f"OCR detected ~{len(texts)} text snippets."
        ],
        "observations": [
            "Image processed and OCR completed.",
            "Trends/insights pending LLM analysis."
        ],
        "improvements": [
            "Ensure chart title and axis labels are readable.",
            "Use high-contrast colors for lines/bars and labels."
        ],
        "ocr_preview": texts[:12],
    }

def analyze_chart(image_path: str, ocr: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    ocr_texts = "\n".join(ocr.get("texts", [])[:50]) or "(no OCR text)"

    if not api_key:
        return _fallback_report(ocr)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": PROMPT_SYS},
                {"role": "user", "content": PROMPT_USER_TMPL.format(ocr_texts=ocr_texts)},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        msg = resp.choices[0].message
        parsed = getattr(msg, "parsed", None)
        if parsed is not None:
            out = parsed
        else:
            import json
            out = json.loads(msg.content)

        out["ocr_preview"] = ocr.get("texts", [])[:12]
        return out
    except Exception as e:
        fb = _fallback_report(ocr)
        fb["summary"][0] = "(LLM error) Could not generate analysis."
        fb["summary"].append(f"Reason: {type(e).__name__}")
        return fb
