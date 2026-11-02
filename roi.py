from dataclasses import dataclass, field

import numpy as np
import cv2

from geometry import rot_matrix_deg, rect_corners
from img_process import RefImgContext
import constants as c


@dataclass
class SingleROI:

    name: str
    offset: tuple
    width: float
    height: float
    rotation_angle: float = 0.0
    OCR_allowlist: str = ""

    def roi_center_at(self, ref_center, delta_angle=0.0):
        R = rot_matrix_deg(delta_angle)
        return np.asarray(ref_center, np.float32) + R @ np.asarray(self.offset, np.float32)

    def corners_at(self, ref_center, delta_angle=0.0):
        roi_center = self.roi_center_at(ref_center, delta_angle)
        angle_rad = np.radians(delta_angle + self.rotation_angle)
        corners = rect_corners(float(roi_center[0]), float(roi_center[1]),
                               self.width, self.height, angle_rad)
        return np.intp(corners), roi_center, rot_matrix_deg(delta_angle + self.rotation_angle)

    def extract(self, frame, ref_center, delta_angle=0.0):
        if frame is None:
            return None

        _, roi_center, R_roi = self.corners_at(ref_center, delta_angle)
        w, h = int(round(self.width)), int(round(self.height))
        if w <= 0 or h <= 0:
            return None

        Rt = R_roi.T
        M = np.zeros((2, 3), np.float32)
        M[:, :2] = Rt
        M[:, 2] = np.array([w / 2, h / 2], np.float32) - Rt @ roi_center

        roi = cv2.warpAffine(frame, M, (w, h),
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
        return roi if roi.size > 0 else None


@dataclass
class MultiROI:

    reference: RefImgContext
    rois: dict = field(default_factory=dict)

    def add(self, roi, replace=False):
        if not replace and roi.name in self.rois:
            raise KeyError("--ERR: MultiROI ROI '%s' already exists" % roi.name)
        self.rois[roi.name] = roi

    def remove(self, name):
        self.rois.pop(name, None)

    def get(self, name):
        return self.rois.get(name)

def render_rois(frame, roi_center, roi_corners, name, width=c.ROI_LINE_WIDTH, color=c.BLUE):
    cv2.polylines(frame, [roi_corners.reshape(-1, 1, 2)], True,
                  color, width)
    cv2.drawMarker(frame, tuple(map(int, roi_center)),
                   color, cv2.MARKER_CROSS, 12, width)
    cv2.putText(frame, name, tuple(map(int, roi_corners[0])),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, c.GREEN, 2, cv2.LINE_AA)
    return frame
    