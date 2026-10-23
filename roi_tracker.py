from dataclasses import dataclass
import numpy as np
import cv2

import constants as c
import funcs as f


@dataclass
class RefState:
    have_ref: bool = False
    ref_center: tuple | None = None
    roi_offset: tuple | None = None
    roi_w: int = 0
    roi_h: int = 0
    ref_frame: np.ndarray | None = None
    prev_angle: float | None = None


def init_reference(frame, f) -> RefState:
    roi_x0, roi_y0, roi_w, roi_h = cv2.selectROI(
        "Select ROI", frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select ROI")

    if roi_w <= 0 or roi_h <= 0:
        return RefState()

    roi_cx = roi_x0 + roi_w / 2
    roi_cy = roi_y0 + roi_h / 2

    ref_bin = f.rgb2bin(frame, low_threshold=160)
    ref_contours = f.external_countur_get(ref_bin)
    if not ref_contours:
        return RefState()

    ref_rect = cv2.minAreaRect(ref_contours[0])
    ref_center = ref_rect[0]

    return RefState(
        have_ref=True,
        ref_center=ref_center,
        roi_offset=(roi_cx - ref_center[0], roi_cy - ref_center[1]),
        roi_w=roi_w,
        roi_h=roi_h,
        ref_frame=frame.copy(),
        prev_angle=None,
    )


def update_roi_tracking(frame, state: RefState, cur_center,
                        do_ocr=False, allowlist=None):
    if not state.have_ref or cur_center is None:
        return state, None

    d_angle = f.get_angle(state.ref_frame, frame, state.prev_angle)
    state.prev_angle = d_angle

    pts, _, _ = f.roi_geometry(
        state.roi_offset, state.roi_w, state.roi_h, cur_center, d_angle)
    cv2.polylines(frame, [pts], True, c.BLUE, 2)

    text = None
    if do_ocr:
        import ocr  # локальный импорт: easyocr грузится только когда нужен
        roi_img = ocr.extract_aligned_roi(frame, state, cur_center, d_angle)
        text = ocr.recognize(roi_img, allowlist=allowlist)

    return state, text