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
    
    def render(self, frame, ref_center, delta_angle=0.0,
               name=None, color=c.BLUE, width=c.ROI_LINE_WIDTH):
        if frame is None:
            return None

        corners, roi_center, _ = self.corners_at(ref_center, delta_angle)
        label = self.name if name is None else name

        vis = frame.copy()
        cv2.polylines(vis, [corners.reshape(-1, 1, 2)], True, color, width)
        cv2.drawMarker(vis, tuple(map(int, roi_center)),
                       color, cv2.MARKER_CROSS, 12, width)
        cv2.putText(vis, label, tuple(map(int, corners[0])),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, c.GREEN, 2, cv2.LINE_AA)
        return vis


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

    # -----------------------------------------------------------------------
    # Bulk operations
    # -----------------------------------------------------------------------
    """
    Draw every ROI of this container on a copy of `frame`.

    See `SingleROI.render` for the meaning of `ref_center`, `delta_angle`,
    `color` and `width`. Each ROI is drawn with its own name label.

    Returns
    -------
    np.ndarray | None
        The annotated copy of `frame`, or None if `frame` is None.
    """
    def render_all(self, frame, ref_center, delta_angle=0.0,
                   color=c.BLUE, width=c.ROI_LINE_WIDTH):
        if frame is None:
            return None
        vis = frame.copy()
        for roi in self.rois.values():
            vis = roi.render(vis, ref_center=ref_center,
                             delta_angle=delta_angle,
                             color=color, width=width)
        return vis

    """
    Extract every ROI of this container from `frame`.

    Parameters
    ----------
    frame : np.ndarray
        Frame to extract from.
    ref_center : (cx, cy)
        Reference-image center (usually `reference.center` or
        `cur_context.center`).
    delta_angle : float
        Rotation of the current frame relative to the reference, degrees.

    Returns
    -------
    dict[str, np.ndarray | None]
        Mapping name -> patch. ROI for which extraction failed
        (None / empty array) are present with value None and a warning
        is printed to stderr.
    """
    def extract_all(self, frame, ref_center, delta_angle=0.0):
        result = {}
        for name, roi in self.rois.items():
            patch = roi.extract(frame, ref_center=ref_center, delta_angle=delta_angle)
            if patch is None or patch.size == 0:
                print(f"--WARN: MultiROI.extract_all failed to extract '{name}'")
                result[name] = None
            else:
                result[name] = patch
        return result
    