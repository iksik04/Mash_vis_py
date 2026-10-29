''' 
Functions working with ROI: create, draw, update
'''

from dataclasses import dataclass, field
import numpy as np
import cv2

import constants as c
import img_process as ip

from roi_selector import select_rotated_roi

'''
ROI geometry
'''
@dataclass
class RoiGeometry:
    offset: tuple
    w: float
    h: float
    angle: float = 0.0

    # calculates ROI geometry (if it is rotated or/and moved)
    def corners(self, cur_center, angle_deg):
        a = np.radians(angle_deg)
        ca, sa = np.cos(a), np.sin(a)
        R = np.array([[ca, -sa], [sa, ca]], dtype=np.float32)

        ox, oy = self.offset
        roi_center = (np.asarray(cur_center, np.float32)
                      + R @ np.array([ox, oy], np.float32))
        
        a_roi = np.radians(angle_deg + self.angle)
        ca, sa = np.cos(a_roi), np.sin(a_roi)
        R_roi = np.array([[ca, -sa], [sa, ca]], dtype=np.float32)

        half = np.array([[-self.w/2, -self.h/2],
                         [ self.w/2, -self.h/2],
                         [ self.w/2,  self.h/2],
                         [-self.w/2,  self.h/2]], dtype=np.float32)
        return np.intp(half @ R_roi.T + roi_center), roi_center, R_roi


'''
Single ROI tracker with its own state
'''
@dataclass
class RoiTracker:
    geometry: RoiGeometry
    name: str = "roi"
    allowlist: str | None = None 
    prev_angle: float | None = None
    last_center: tuple | None = None
    last_angle: float | None = None
    lost: bool = False

    @property
    def ready(self) -> bool:
        return True

    def update_angle(self, raw_angle: float) -> float:
        if not np.isfinite(raw_angle):
            return self.prev_angle if self.prev_angle is not None else 0.0
        if self.prev_angle is not None:
            raw_angle = self.prev_angle + ((raw_angle - self.prev_angle + 180) % 360) - 180
        self.prev_angle = raw_angle
        return raw_angle

    def tick(self, ctx: 'ip.FrameContext', raw_angle: float) -> bool:
        if ctx.center is None or not np.isfinite(raw_angle):
            self.lost = True
            return False
        self.last_angle = self.update_angle(raw_angle)
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
    reference: ip.Reference | None = None
    def add(self, tracker: RoiTracker) -> None:
        self.trackers[tracker.name] = tracker

    def remove(self, name: str) -> None:
        self.trackers.pop(name, None)

    def __getitem__(self, name: str) -> RoiTracker:
        return self.trackers[name]

    def __len__(self) -> int:
        return len(self.trackers)

    def ready(self) -> bool:
        return self.reference is not None and bool(self.trackers)

    def process(self, ctx: 'ip.FrameContext') -> dict[str, bool]:
        if self.reference is None or ctx.center is None:
            for t in self.trackers.values():
                t.lost = True
            return {n: False for n in self.trackers}

        raw_angle = ip.get_angle(self.reference.image, ctx.frame)
        return {n: t.tick(ctx, raw_angle) for n, t in self.trackers.items()}

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


def init_reference(frame, ref_center, name="roi", allowlist=None) -> RoiTracker | None:
    win = f"Select ROI [{name}]"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.imshow(win, frame)
    cv2.waitKey(1)

    sel = select_rotated_roi(win, frame)
    cv2.destroyWindow(win)
    if sel is None:
        return None

    x0, y0, w, h, angle_deg = sel
    if w <= 0 or h <= 0:
        return None


    a = np.radians(angle_deg)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]], np.float32)
    roi_center = np.array([x0, y0], np.float32) - R @ np.array([-w/2, -h/2], np.float32)

    offset = (float(roi_center[0] - ref_center[0]),
              float(roi_center[1] - ref_center[1]))

    return RoiTracker(
        name=name,
        geometry=RoiGeometry(offset=offset, w=float(w), h=float(h), angle=float(angle_deg)),
        allowlist=allowlist,
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