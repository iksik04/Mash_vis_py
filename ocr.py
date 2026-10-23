import cv2
import numpy as np
import easyocr

_reader = None

# creates ocr reader (once for a programm)
def get_reader(langs=('ru', 'en'), gpu=False):
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(list(langs), gpu=gpu)
    return _reader

# upscale + rgb2gr preprocess for OCR
def preprocess_for_ocr(roi, scale=3):
    big = cv2.resize(roi, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    return gray


def recognize(roi, allowlist=None):
    if roi is None or roi.size == 0:
        return None
    img = preprocess_for_ocr(roi)
    reader = get_reader()
    res = reader.readtext(img, detail=0, allowlist=allowlist)
    return res[0] if res else None