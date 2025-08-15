# explain_graph/visualize.py
from __future__ import annotations
from typing import Tuple
import cv2
import numpy as np
from pathlib import Path

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

def _bar_rects(thresh: np.ndarray) -> list[Tuple[int,int,int,int]]:
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        if area < 200:
            continue
        aspect = h / (w + 1e-6)
        if aspect > 1.7 and h > 25:
            rects.append((x, y, w, h))
    return rects

def _line_segments(edges: np.ndarray, min_len: int = 40):
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=60,
                            minLineLength=min_len, maxLineGap=8)
    return [] if lines is None else lines[:,0,:]  # (x1,y1,x2,y2)

def _blob_keypoints(gray: np.ndarray):
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 15
    params.maxArea = 600
    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = False
    detector = cv2.SimpleBlobDetector_create(params)
    kps = detector.detect(gray)
    return [] if kps is None else kps

def draw_overlay(image_path: str, save_path: str) -> str:
    """
    Saves an overlay PNG highlighting:
      - Bars (green rectangles)
      - Line segments (red lines)
      - Scatter-like blobs (blue circles)
    Returns the saved path.
    """
    bgr = _load_bgr(image_path)
    out = bgr.copy()
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # Threshold for bars
    thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY_INV, 31, 7)
    edges = _prep_edges(gray)

    rects = _bar_rects(thr)
    lines = _line_segments(edges)
    blobs = _blob_keypoints(gray)

    # Draw bars (green)
    for (x, y, w, h) in rects:
        cv2.rectangle(out, (x, y), (x+w, y+h), (0, 200, 0), 2)

    # Draw lines (red)
    for (x1, y1, x2, y2) in lines:
        cv2.line(out, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # Draw blobs (blue)
    for kp in blobs:
        x, y = int(kp.pt[0]), int(kp.pt[1])
        r = int(kp.size / 2)
        cv2.circle(out, (x, y), r, (255, 0, 0), 2)

    save_p = Path(save_path)
    save_p.parent.mkdir(parents=True, exist_ok=True)
    # Use cv2.imencode to support Windows paths robustly
    ok, buf = cv2.imencode(".png", out)
    if not ok:
        raise RuntimeError("Failed to encode overlay PNG.")
    save_p.write_bytes(buf.tobytes())
    return str(save_p.resolve())
