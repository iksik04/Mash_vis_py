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

# cuts aligned ROI from frame
def extract_aligned_roi(frame, state, cur_center, d_angle):
    import roi
    if state.roi_w <= 0 or state.roi_h <= 0 or state.roi_offset is None:
        return None

    _, roi_center, R = roi.roi_geometry(
        state.roi_offset, state.roi_w, state.roi_h, cur_center, d_angle)

    # p_roi = R^T @ (p_frame - roi_center) + [w/2, h/2]
    Rt = R.T
    M = np.zeros((2, 3), dtype=np.float32)
    M[:, :2] = Rt
    M[:, 2]  = np.array([state.roi_w / 2.0, state.roi_h / 2.0],
                        dtype=np.float32) - Rt @ roi_center

    roi = cv2.warpAffine(frame, M, (int(state.roi_w), int(state.roi_h)),
                         flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REPLICATE)
    return roi if roi.size > 0 else None

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
    res = _reader.readtext(img, detail=0, allowlist=allowlist)
    return res[0] if res else None