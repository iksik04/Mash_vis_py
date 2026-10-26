''' 
Functions working with ROI: create, draw, update
'''

from dataclasses import dataclass, field
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
Single ROI tracker with its own state
'''
@dataclass
class RoiTracker:
    geometry: RoiGeometry
    name: str = "roi"
    reference: Reference | None = None
    prev_angle: float | None = None
    last_center: tuple | None = None
    last_angle: float | None = None
    lost: bool = False

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

    def tick(self, ctx: 'ip.FrameContext') -> bool:
        if not self.ready or ctx.center is None:
            self.lost = True
            return False

        raw = ip.get_angle(self.reference.image, ctx.frame)
        self.last_angle = self.update_angle(raw)
        self.last_center = ctx.center
        self.lost = False
        return True

    def corners(self):
        if self.last_center is None:
            return None, None, None
        return self.geometry.corners(self.last_center, self.last_angle or 0.0)


'''
Set of named ROI trackers + per-frame orchestration
'''
@dataclass
class RoiSet:
    trackers: dict[str, RoiTracker] = field(default_factory=dict)

    def add(self, tracker: RoiTracker) -> None:
        self.trackers[tracker.name] = tracker

    def remove(self, name: str) -> None:
        self.trackers.pop(name, None)

    def __getitem__(self, name: str) -> RoiTracker:
        return self.trackers[name]

    def __len__(self) -> int:
        return len(self.trackers)

    def ready(self) -> bool:
        return bool(self.trackers) and all(t.ready for t in self.trackers.values())

    def process(self, ctx: 'ip.FrameContext') -> dict[str, bool]:
        return {name: t.tick(ctx) for name, t in self.trackers.items()}

    def draw(self, frame, color=c.BLUE, width=c.ROI_LINE_WIDTH) -> None:
        for t in self.trackers.values():
            pts, _, _ = t.corners()
            if pts is None:
                continue
            cv2.polylines(frame, [pts], True, color, width)

    def extract(self, frame) -> dict[str, np.ndarray | None]:
        return {
            name: (extract_aligned_roi(frame, t) if not t.lost else None)
            for name, t in self.trackers.items()
        }

'''
init ref ROI (select on the image)
'''
def init_reference(frame, name: str = "roi") -> RoiTracker | None:
    x0, y0, w, h = cv2.selectROI("Select ROI", frame, True, False)
    cv2.destroyWindow("Select ROI")
    if w <= 0 or h <= 0:
        return None

    contour = ip.get_main_contour(
        ip.rgb2bin(frame, low_threshold=c.BINARYSATION_LOW_THRESHOLD)
    )
    if contour is None:
        return None

    ref_center = cv2.minAreaRect(contour)[0]
    roi_cx, roi_cy = x0 + w / 2, y0 + h / 2

    return RoiTracker(
        name=name,
        geometry=RoiGeometry(
            offset=(roi_cx - ref_center[0], roi_cy - ref_center[1]),
            w=float(w), h=float(h)),
        reference=Reference(frame.copy(), ref_center),
    )

'''
Draw single ROI (kept for backward compatibility).
Does NOT compute angle — requires tracker.tick() called before.
'''
def draw_roi(frame, tracker: RoiTracker) -> None:
    if tracker is None or not tracker.ready:
        return
    pts, _, _ = tracker.corners()
    if pts is None:
        return
    cv2.polylines(frame, [pts], True, c.BLUE, 2)

'''
cuts aligned ROI from frame (angle/center taken from tracker state)
'''
def extract_aligned_roi(frame, tracker: RoiTracker):
    if tracker is None or not tracker.ready or tracker.last_center is None:
        return None

    _, roi_center, R = tracker.geometry.corners(
        tracker.last_center, tracker.last_angle or 0.0)
    w, h = int(tracker.geometry.w), int(tracker.geometry.h)

    Rt = R.T
    M = np.zeros((2, 3), np.float32)
    M[:, :2] = Rt
    M[:, 2] = np.array([w / 2, h / 2], np.float32) - Rt @ roi_center

    roi = cv2.warpAffine(frame, M, (w, h), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REPLICATE)
    return roi if roi.size > 0 else None