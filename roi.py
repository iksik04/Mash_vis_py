from dataclasses import dataclass, field

import numpy as np
import cv2

from geometry import rot_matrix_deg, rect_corners, side_midpoints
from img_process import RefImgContext


@dataclass
class SingleROI:

    name: str
    offset: tuple
    width: float
    height: float
    rotation_angle: float = 0.0
    OCR_allowlist: str = ""

    def _rotation_matrix(self, angle_deg):
        return rot_matrix_deg(angle_deg)

    def roi_center_at(self, ref_center, delta_angle=0.0):
        R = self._rotation_matrix(delta_angle)
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
    last_angle: float = None

    def add(self, roi, replace=False):
        if not replace and roi.name in self.rois:
            raise KeyError("--ERR: MultiROI ROI '%s' already exists" % roi.name)
        self.rois[roi.name] = roi

    def remove(self, name):
        self.rois.pop(name, None)

    def get(self, name):
        return self.rois.get(name)