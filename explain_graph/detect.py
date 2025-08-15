# explain_graph/detect.py
from __future__ import annotations
from typing import Dict, Any
from dataclasses import dataclass
import cv2
import numpy as np


@dataclass
class ChartGuess:
    chart_type: str              # "bar" | "line" | "scatter" | "unknown"
    features: Dict[str, Any]     # simple counts & cues for LLM prompt

def _load_bgr(path: str) -> np.ndarray:
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {path}")
    return img

def _prep_edges(gray: np.ndarray) -> np.ndarray:
    g = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(g, 50, 150)
    return edges

def _count_rect_bars(thresh: np.ndarray) -> int:
    # Count tall, thin-ish contours as "bars"
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bars = 0
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        if area < 200:          # ignore tiny specks
            continue
        aspect = h / (w + 1e-6)
        if aspect > 1.7 and h > 25:
            bars += 1
    return bars

def _count_line_segments(edges: np.ndarray, min_len: int = 40) -> int:
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=60,
                            minLineLength=min_len, maxLineGap=8)
    return 0 if lines is None else len(lines)

def _count_blobs(gray: np.ndarray) -> int:
    # Detect small circular-ish blobs (scatter points)
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 15
    params.maxArea = 600
    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = False
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(gray)
    return 0 if keypoints is None else len(keypoints)

def detect_chart_type(image_path: str) -> ChartGuess:
    bgr = _load_bgr(image_path)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # Binary for rectangles (bars)
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY_INV, 31, 7)
    edges = _prep_edges(gray)

    bars = _count_rect_bars(thr)
    lines = _count_line_segments(edges)
    blobs = _count_blobs(gray)

    # Naive rule-of-thumb voting
    # - Many tall rectangles → bar
    # - Many line segments (including axis + series) → line
    # - Many blobs → scatter
    # Thresholds are heuristic and may be tuned
    votes = {
        "bar": int(bars >= 3 and bars >= lines and bars >= blobs),
        "line": int(lines >= 25 and lines >= bars and lines >= blobs),
        "scatter": int(blobs >= 25 and blobs >= lines and blobs >= bars),
    }
    chart_type = "unknown"
    if votes["bar"]: chart_type = "bar"
    if votes["line"]: chart_type = "line"
    if votes["scatter"]: chart_type = "scatter"

    return ChartGuess(
        chart_type=chart_type,
        features={
            "bar_like_rectangles": bars,
            "line_segments": lines,
            "point_like_blobs": blobs,
            "image_shape": bgr.shape[:2],
        }
    )
