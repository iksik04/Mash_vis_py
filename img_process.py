import cv2
import numpy as np
from dataclasses import dataclass

'''
keeps info about reference image
'''
@dataclass
class RefImgContext:
    bgr_img: np.ndarray
    ref_low_threshold: int
    min_ext_contour_length: float

    bin_img: np.ndarray | None = None
    ext_contour: np.ndarray | None = None
    center: tuple | None = None

    def build_ref_context(self):
        gray_img = cv2.cvtColor(self.bgr_img, cv2.COLOR_BGR2GRAY)
        _, self.bin_img  = cv2.threshold(gray_img,
                                    self.ref_low_threshold,
                                    255,
                                    cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(self.bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = []
        for cnt in contours:
            length = cv2.arcLength(cnt, True)
            if length >= self.min_ext_contour_length:
                filtered_contours.append(cnt)
        if len(filtered_contours) == 0:
            raise ValueError("--ERR: RefImgContext.build_ref_context no contours found")
        else:
            self.ext_contour = max(filtered_contours, key=lambda c: cv2.arcLength(c, True))
            self.center = cv2.minAreaRect(self.ext_contour)[0]

    def __repr__(self) -> str:
        def arr_info(a):
            return "None" if a is None else f"ndarray(shape={a.shape}, dtype={a.dtype})"

        def contour_info(c):
            return "None" if c is None else f"contour(points={len(c)}, shape={c.shape})"

        return (
            f"{type(self).__name__}(\n"
            f"  bgr_img            = {arr_info(self.bgr_img)},\n"
            f"  bin_img            = {arr_info(self.bin_img)},\n"
            f"  ext_contour        = {contour_info(self.ext_contour)},\n"
            f"  center             = {self.center},\n"
            f"  ref_low_threshold  = {self.ref_low_threshold},\n"
            f"  min_ext_contour_length = {self.min_ext_contour_length},\n"
            f")"
        )


    
'''
keeps info about current image
'''
@dataclass
class CurImgContext:
    bgr_img: np.ndarray

    ref_low_threshold: int
    min_ext_contour_length: float

    delta_angle: float | None = None

    reference: RefImgContext | None = None
    bin_img: np.ndarray | None = None
    ext_contour: np.ndarray | None = None
    center: tuple | None = None

    def build_cur_context(self):
        gray_img = cv2.cvtColor(self.bgr_img, cv2.COLOR_BGR2GRAY)
        _, self.bin_img  = cv2.threshold(gray_img,
                                    self.ref_low_threshold,
                                    255,
                                    cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(self.bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = []
        for cnt in contours:
            length = cv2.arcLength(cnt, True)
            if length >= self.min_ext_contour_length:
                filtered_contours.append(cnt)
        if len(filtered_contours) == 0:
            raise ValueError("--ERR: RefImgContext.build_ref_context no contours found")
        else:
            self.ext_contour = max(filtered_contours, key=lambda c: cv2.arcLength(c, True))
            self.center = cv2.minAreaRect(self.ext_contour)[0]

        if self.reference is not None:
            self.delta_angle = get_angle(self.reference.bgr_img, self.bgr_img)
            if not np.isnan(self.delta_angle):
                while self.delta_angle <= -180:
                    self.delta_angle += 360
                while self.delta_angle > 180:
                    self.delta_angle -= 360


    def __repr__(self) -> str:
        def arr_info(a):
            return "None" if a is None else f"ndarray(shape={a.shape}, dtype={a.dtype})"

        def contour_info(c):
            return "None" if c is None else f"contour(points={len(c)}, shape={c.shape})"

        ref_info = "None" if self.reference is None else type(self.reference).__name__
        return (
            f"{type(self).__name__}(\n"
            f"  reference          = {ref_info},\n"
            f"  bgr_img            = {arr_info(self.bgr_img)},\n"
            f"  bin_img            = {arr_info(self.bin_img)},\n"
            f"  ext_contour        = {contour_info(self.ext_contour)},\n"
            f"  center             = {self.center},\n"
            f"  ref_low_threshold  = {self.ref_low_threshold},\n"
            f"  min_ext_contour_length = {self.min_ext_contour_length},\n"
            f"  delta_angle        = {self.delta_angle},\n"
            f")"
        )

def get_angle(img1, img2):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        print("--ERR: get_angle des1 or des2 is None")
        return float('nan')

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    matches = matches[:50]
    if not matches:
        print("--ERR: get_angle matches is False")
        return float('nan')

    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    M, _ = cv2.estimateAffinePartial2D(src_pts, dst_pts)
    if M is None:
        print("--ERR: get_angle M is None")
        return float('nan')

    return float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
