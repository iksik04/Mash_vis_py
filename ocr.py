import cv2
import numpy as np
import easyocr

_reader = None

def get_reader(langs=('ru', 'en'), gpu=False):
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(list(langs), gpu=gpu)
    return _reader


def extract_aligned_roi(frame, state, cur_center, d_angle):
    if state.roi_w <= 0 or state.roi_h <= 0 or state.roi_offset is None:
        return None

    # нормализуем накопленный угол в (-180, 180]
    a = ((d_angle + 180.0) % 360.0) - 180.0

    h_img, w_img = frame.shape[:2]
    cx_obj, cy_obj = cur_center

    rad = np.radians(a)
    cos_a, sin_a = np.cos(rad), np.sin(rad)
    ox, oy = state.roi_offset
    roi_cx = cx_obj + ox * cos_a - oy * sin_a
    roi_cy = cy_obj + ox * sin_a + oy * cos_a

    diag = int(np.hypot(state.roi_w, state.roi_h) / 2) + 8
    x0 = max(int(roi_cx) - diag, 0)
    y0 = max(int(roi_cy) - diag, 0)
    x1 = min(int(roi_cx) + diag, w_img)
    y1 = min(int(roi_cy) + diag, h_img)
    patch = frame[y0:y1, x0:x1]
    if patch.size == 0:
        return None

    local_cx, local_cy = roi_cx - x0, roi_cy - y0
    # ВАЖНО: +a (знак поменяли с -d_angle на +a)
    M = cv2.getRotationMatrix2D((local_cx, local_cy), a, 1.0)
    h, w = patch.shape[:2]
    rotated = cv2.warpAffine(patch, M, (w, h),
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)

    rcx, rcy = int(local_cx), int(local_cy)
    hw, hh = state.roi_w // 2, state.roi_h // 2
    x_start, y_start = rcx - hw, rcy - hh
    x_end, y_end = x_start + state.roi_w, y_start + state.roi_h

    pad_l = max(-x_start, 0); pad_t = max(-y_start, 0)
    pad_r = max(x_end - w, 0); pad_b = max(y_end - h, 0)
    if pad_l or pad_t or pad_r or pad_b:
        rotated = cv2.copyMakeBorder(rotated, pad_t, pad_b, pad_l, pad_r,
                                     cv2.BORDER_REPLICATE)
        x_start += pad_l; y_start += pad_t
        x_end += pad_l; y_end += pad_t

    roi = rotated[y_start:y_end, x_start:x_end]
    return roi if roi.size > 0 else None


def preprocess_for_ocr(roi, scale=3):
    """Апскейл + серое. EasyOCR лучше работает с серым, чем с жесткой бинаризацией."""
    big = cv2.resize(roi, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
    # мягкая нормализация контраста — помогает на неравномерном свете
    gray = cv2.equalizeHist(gray)
    return gray


def recognize(roi, allowlist=None, langs=('ru', 'en')):
    if roi is None or roi.size == 0:
        return None
    img = preprocess_for_ocr(roi)
    reader = get_reader(langs)
    res = reader.readtext(img, detail=0, allowlist=allowlist)
    return res[0] if res else None