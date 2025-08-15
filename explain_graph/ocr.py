from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
import cv2
import numpy as np
import easyocr

def _read_image(path: str) -> np.ndarray:
    img = cv2.imdecode(np.fromfile(Path(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        # fallback: cv2.imread if filesystem supports it normally
        img = cv2.imread(str(Path(path)))
    if img is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return img

def _prep_for_ocr(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # mild denoise + adaptive threshold to help OCR on charts
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                               cv2.THRESH_BINARY, 31, 7)
    return th

def ocr_extract(image_path: str, lang: str = "en") -> Dict[str, Any]:
    img = _read_image(image_path)
    th = _prep_for_ocr(img)

    # EasyOCR works directly on RGB; convert thresholded to 3-channel
    th_rgb = cv2.cvtColor(th, cv2.COLOR_GRAY2RGB)
    reader = easyocr.Reader([lang], gpu=False)  # CPU-friendly
    results = reader.readtext(th_rgb)  # list of [bbox, text, confidence]

    texts: List[str] = []
    boxes: List = []
    confs: List[float] = []
    for bbox, text, conf in results:
        t = text.strip()
        if t:
            texts.append(t)
            boxes.append(bbox)
            confs.append(float(conf))

    return {
        "texts": texts,
        "boxes": boxes,
        "confs": confs,
        "shape": img.shape[:2],
    }
