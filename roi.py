''' 
Functions working with ROI: create, draw, update
'''

from dataclasses import dataclass
import numpy as np
import cv2

import constants as c
import img_process as ip

# State of ROI
@dataclass
class RefState:
    have_ref: bool = False
    ref_center: tuple | None = None
    roi_offset: tuple | None = None
    roi_w: int = 0
    roi_h: int = 0
    ref_frame: np.ndarray | None = None
    prev_angle: float | None = None

# init ref ROI (select on the image)
def init_reference(frame) -> RefState:
    roi_x0, roi_y0, roi_w, roi_h = cv2.selectROI(
        "Select ROI", frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select ROI")

    if roi_w <= 0 or roi_h <= 0:
        return RefState()

    roi_cx = roi_x0 + roi_w / 2
    roi_cy = roi_y0 + roi_h / 2

    ref_bin = ip.rgb2bin(frame, low_threshold=160)
    ref_contours = ip.external_countur_get(ref_bin)
    if len(ref_contours) > 0:
            ref_contours = ref_contours[0]
    else: return RefState()

    ref_rect = cv2.minAreaRect(ref_contours)
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

# calculates ROI geometry (if it is rotated or/and moved)
def roi_geometry(roi_offset, roi_w, roi_h, cur_center, angle_deg):
    """
      - angle_deg > 0 — rotation against clock arrow in frame coordinates
      - Rotation matrix R = [[cos, -sin], [sin, cos]]
      - roi_offset is setted in object coordinate system

    retival:
      corners    — (4, 2) np.intp, ROI in frame coord
      roi_center — (2,) np.float32, center ROI 
      R          — (2, 2) np.float32, ritation matrix
    """
    a = np.radians(angle_deg)
    ca, sa = np.cos(a), np.sin(a)
    R = np.array([[ca, -sa],
                  [sa,  ca]], dtype=np.float32)

    ox, oy = roi_offset
    roi_center = (np.asarray(cur_center, dtype=np.float32)
                  + R @ np.array([ox, oy], dtype=np.float32))

    half = np.array([[-roi_w / 2.0, -roi_h / 2.0],
                     [ roi_w / 2.0, -roi_h / 2.0],
                     [ roi_w / 2.0,  roi_h / 2.0],
                     [-roi_w / 2.0,  roi_h / 2.0]], dtype=np.float32)

    corners = half @ R.T + roi_center          # (4, 2)
    return np.intp(corners), roi_center, R

def update_roi_tracking(frame, state: RefState, cur_center,
                        do_ocr=False, allowlist=None):
    if not state.have_ref or cur_center is None:
        return state, None

    d_angle = ip.get_angle(state.ref_frame, frame, state.prev_angle)
    state.prev_angle = d_angle

    pts, _, _ = roi_geometry(
        state.roi_offset, state.roi_w, state.roi_h, cur_center, d_angle)
    cv2.polylines(frame, [pts], True, c.BLUE, 2)

    text = None
    if do_ocr:
        import ocr
        roi_img = ocr.extract_aligned_roi(frame, state, cur_center, d_angle)
        text = ocr.recognize(roi_img, allowlist=allowlist)

    return state, text