from dataclasses import dataclass, field
import numpy as np
import cv2

from img_process import RefImgContext

@dataclass
class SingleROI:

    name: str
    offset: tuple[float, float]
    width: float
    heigth: float
    rotation_angle: float = 0.0
    OCR_allowlist: str = ""

    def _rotation_matrix(self, angle_deg: float) -> np.ndarray:
        a = np.radians(angle_deg)
        ca, sa = np.cos(a), np.sin(a)
        return np.array([[ca, -sa], [sa, ca]], dtype=np.float32)

    def roi_center_at(self, ref_center, delta_angle: float = 0.0) -> np.ndarray:
        R = self._rotation_matrix(delta_angle)
        return np.asarray(ref_center, np.float32) + R @ np.asarray(self.offset, np.float32)

    def corners_at(self, ref_center, delta_angle: float = 0.0):

        roi_center = self.roi_center_at(ref_center, delta_angle)

        a_roi = np.radians(delta_angle + self.rotation_angle)
        ca, sa = np.cos(a_roi), np.sin(a_roi)
        R_roi = np.array([[ca, -sa], [sa, ca]], dtype=np.float32)

        hw, hh = self.width / 2.0, self.height / 2.0
        half = np.array([[-hw, -hh],
                         [ hw, -hh],
                         [ hw,  hh],
                         [-hw,  hh]], dtype=np.float32)
        pts = half @ R_roi.T + roi_center
        return np.intp(pts), roi_center, R_roi

    def extract(self, frame, ref_center, delta_angle: float = 0.0):

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
    rois: dict[str, SingleROI] = field(default_factory=dict)
    last_angle: float | None = None

    def add(self, roi: SingleROI, replace: bool = False) -> None:
        if not replace and roi.name in self.rois:
            raise KeyError(f"--ERR: MultiROI ROI '{roi.name}' already exists")
        self.rois[roi.name] = roi

    def remove(self, name: str) -> None:
        self.rois.pop(name, None)

    def get(self, name: str) -> SingleROI | None:
        return self.rois.get(name)