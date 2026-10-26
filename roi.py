''' 
Functions working with ROI: create, draw, update
'''

from dataclasses import dataclass
import numpy as np
import cv2

import constants as c
import img_process as ip

'''
ROI geometry
'''
@dataclass
class RoiGeometry:
    offset: tuple
    w: float
    h: float

    # calculates ROI geometry (if it is rotated or/and moved)
    def corners(self, cur_center, angle_deg):
        a = np.radians(angle_deg)
        ca, sa = np.cos(a), np.sin(a)
        R = np.array([[ca, -sa], [sa, ca]], dtype=np.float32)

        ox, oy = self.offset
        roi_center = (np.asarray(cur_center, np.float32)
                      + R @ np.array([ox, oy], np.float32))

        half = np.array([[-self.w/2, -self.h/2],
                         [ self.w/2, -self.h/2],
                         [ self.w/2,  self.h/2],
                         [-self.w/2,  self.h/2]], dtype=np.float32)
        return np.intp(half @ R.T + roi_center), roi_center, R

'''
Reference image, center is a center of biggest contour
'''
@dataclass
class Reference:
    image: np.ndarray
    center: tuple

'''
Collect together ROI geometry and ref
'''
@dataclass
class RoiTracker:
    geometry: RoiGeometry
    reference: Reference | None = None
    prev_angle: float | None = None

    @property
    def ready(self) -> bool:
        return self.reference is not None

    def update_angle(self, raw_angle: float) -> float:
        if not np.isfinite(raw_angle):
            return self.prev_angle if self.prev_angle is not None else 0.0
        if self.prev_angle is not None:
            raw_angle = self.prev_angle + ((raw_angle - self.prev_angle + 180) % 360) - 180
        self.prev_angle = raw_angle
        return raw_angle

'''
for several ROIs
'''
'''
@dataclass
class RoiSet:
    trackers: dict[str, RoiTracker] = field(default_factory=dict)

    def add(self, key: str, tracker: RoiTracker) -> None:
        self.trackers[key] = tracker

    def ready(self) -> bool:
        return all(t.ready for t in self.trackers.values())

    def draw_all(self, frame, cur_center) -> None:
        for t in self.trackers.values():
            draw_roi(frame, t, cur_center)

    def update_angles(self, frame) -> None:
        raw = ip.get_angle(...)  # считается один раз на кадр
        for t in self.trackers.values():
            t.update_angle(raw)
'''

'''
init ref ROI (select on the image)
'''
def init_reference(frame) -> RoiTracker | None:
    x0, y0, w, h = cv2.selectROI("Select ROI", frame, True, False)
    cv2.destroyWindow("Select ROI")
    if w <= 0 or h <= 0:
        return None

    contours = ip.external_countur_get(ip.rgb2bin(frame, low_threshold=c.BINARYSATION_LOW_THRESHOLD))
    contours = ip.longest_contour(contours)
    if contours is None or len(contours) == 0:
        return None

    ref_center = cv2.minAreaRect(contours)[0]
    roi_cx, roi_cy = x0 + w / 2, y0 + h / 2

    return RoiTracker(
        geometry=RoiGeometry(
            offset=(roi_cx - ref_center[0], roi_cy - ref_center[1]),
            w=float(w), h=float(h)),
        reference=Reference(frame.copy(), ref_center),
    )

def draw_roi(frame, tracker: RoiTracker, cur_center):
    if tracker is None or not tracker.ready or cur_center is None:
        return tracker
    d_angle = tracker.update_angle(ip.get_angle(tracker.reference.image, frame))
    pts, _, _ = tracker.geometry.corners(cur_center, d_angle)
    cv2.polylines(frame, [pts], True, c.BLUE, 2)
    return tracker

'''
cuts aligned ROI from frame
'''
def extract_aligned_roi(frame, tracker: RoiTracker, cur_center, d_angle):
    if tracker is None or not tracker.ready:
        return None

    _, roi_center, R = tracker.geometry.corners(cur_center, d_angle)
    w, h = int(tracker.geometry.w), int(tracker.geometry.h)

    Rt = R.T
    M = np.zeros((2, 3), np.float32)
    M[:, :2] = Rt
    M[:, 2] = np.array([w / 2, h / 2], np.float32) - Rt @ roi_center

    roi = cv2.warpAffine(frame, M, (w, h), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REPLICATE)
    return roi if roi.size > 0 else None