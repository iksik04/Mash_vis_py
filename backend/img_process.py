import cv2
import numpy as np
from dataclasses import dataclass

from . import geometry
from . import constants as c

def _arr_info(a):
    return "None" if a is None else f"ndarray(shape={a.shape}, dtype={a.dtype})"
def _contour_info(c):
    return "None" if c is None else f"contour(points={len(c)}, shape={c.shape})"


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
        self.bin_img, self.ext_contour, self.center = extract_main_contour(
            self.bgr_img, self.ref_low_threshold, self.min_ext_contour_length
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(\n"
            f"  bgr_img            = {_arr_info(self.bgr_img)},\n"
            f"  bin_img            = {_arr_info(self.bin_img)},\n"
            f"  ext_contour        = {_contour_info(self.ext_contour)},\n"
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
        self.bin_img, self.ext_contour, self.center = extract_main_contour(
            self.bgr_img, self.ref_low_threshold, self.min_ext_contour_length
        )

        if self.reference is not None:
            self.delta_angle = geometry.normalize_angle_deg(
                get_angle(self.reference.bgr_img, self.bgr_img)
            )

    def __repr__(self) -> str:
        ref_info = "None" if self.reference is None else type(self.reference).__name__
        return (
            f"{type(self).__name__}(\n"
            f"  reference          = {ref_info},\n"
            f"  bgr_img            = {_arr_info(self.bgr_img)},\n"
            f"  bin_img            = {_arr_info(self.bin_img)},\n"
            f"  ext_contour        = {_contour_info(self.ext_contour)},\n"
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

'''
renders image. Countur, rectangle and center are optional
'''
def render_img(image, contours=None, rectangle=False, center=False,
             contour_color=c.GREEN, contour_width=c.CONTOUR_LINE_WIDTH,
             rect_color=c.GREEN, rect_width=c.RECT_LINE_WIDTH,
             center_color=c.GREEN, center_size=None, center_width=c.CENTER_LINE_WIDTH
            ):

    if contours is None:
        contours = []
    elif isinstance(contours, np.ndarray):
        contours = [contours] if contours.ndim in (2, 3) and contours.shape[-1] == 2 else list(contours)
    else:
        contours = list(contours)

    if len(contours) == 0:
        contours = None

    if len(image.shape) == 2:
        canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        canvas = image.copy()

    if contours is not None:
        cv2.drawContours(canvas, contours, -1, contour_color, contour_width)
    else:
        rectangle = False
        center = False

    if rectangle:
        rect = cv2.minAreaRect(max(contours, key=lambda c: cv2.arcLength(c, True)))
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        cv2.drawContours(canvas, [box], 0, rect_color, rect_width)

    if center:
        if not rectangle: rect = cv2.minAreaRect(max(contours, key=lambda c: cv2.arcLength(c, True)))
        (cx, cy), (w, h), _ = rect
        cx, cy = int(cx), int(cy)
        if center_size is None:
            if rect is not None:
                center_size = int(min(w, h) / 20)
            else:
                center_size = 100
        cv2.line(canvas, (cx - center_size, cy), (cx + center_size, cy),
                 center_color, center_width)
        cv2.line(canvas, (cx, cy - center_size), (cx, cy + center_size),
                 center_color, center_width)
    return canvas

def _render_roi_contours(patch, contours, main_cnt, name, thr, min_len, scale=5):
    vis = cv2.resize(patch, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    if len(vis.shape) == 2:
        vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)
    if contours:
        scaled = [ (cnt * scale).astype(np.int32) for cnt in contours ]
        cv2.drawContours(vis, scaled, -1, c.GREEN, c.CONTOUR_LINE_WIDTH)
    if main_cnt is not None:
        scaled_main = (main_cnt * scale).astype(np.int32)
        cv2.drawContours(vis, [scaled_main], -1, c.BLUE, c.RECT_LINE_WIDTH)
    cv2.putText(vis, f"{name}  thr={thr}  min_len={int(min_len)}",
                (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, c.GREEN, 2, cv2.LINE_AA)
    return vis

"""
Binarize the image, find external contours, filter by arc length,
and return (bin_img, ext_contour, center) of the longest contour.
"""
def extract_main_contour(bgr_img, low_threshold, min_length):
    if bgr_img.ndim == 2:
        gray_img = bgr_img
    else: 
        gray_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)

    _, bin_img = cv2.threshold(gray_img, low_threshold, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = [
        cnt for cnt in contours
        if cv2.arcLength(cnt, True) >= min_length
    ]
    if not filtered_contours:
        raise ValueError("--ERR: _extract_main_contour no contours found")

    ext_contour = max(filtered_contours, key=lambda c: cv2.arcLength(c, True))
    center = cv2.minAreaRect(ext_contour)[0]
    return bin_img, ext_contour, center

"""
Find contours, filter by arc length,
and return list contours.
"""
def extract_contours(bin_img, min_length):
    contours, _ = cv2.findContours(bin_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = [
        cnt for cnt in contours
        if cv2.arcLength(cnt, True) >= min_length
    ]
    if not filtered_contours:
        print("--ERR: extract_main_contour no contours found")

    return filtered_contours

def extract_contours_from_bgr(bgr_img, low_threshold, min_length):
    if bgr_img.ndim == 2:
        gray = bgr_img
    else:
        gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
    _, bin_img = cv2.threshold(gray, low_threshold, 255, cv2.THRESH_BINARY)
    return extract_contours(bin_img, min_length), bin_img

"""
Pick the main (longest) contour from `contours`, ignoring contours whose
bounding box covers the whole patch (border frame).

Returns the selected contour, or None if nothing suitable is found.
"""
def pick_main_contour(contours, patch_w, patch_h):
    if not contours:
        return None
    border = np.array([[0,0],[patch_w-1,0],[patch_w-1,patch_h-1],[0,patch_h-1]], np.float32)
    filtered = []
    for cnt in contours:
        # контур считается «рамкой», если его bbox совпадает с bbox патча
        x, y, w, h = cv2.boundingRect(cnt)
        if w >= patch_w - 1 and h >= patch_h - 1:
            continue
        filtered.append(cnt)
    if not filtered:
        return None
    return max(filtered, key=lambda c: cv2.arcLength(c, True))

"""
Sharpen `frame` via detail enhancement and an optional unsharp kernel.

`k` scales the laplacian-style sharpening kernel.
"""
def img_sharpen(frame, k):

    sharpened = cv2.detailEnhance(frame, sigma_s=10, sigma_r=0.15)

    
    kernel = np.array([[ 0, -k,  0],
                   [-k,  1+4*k, -k],
                   [ 0, -k,  0]], np.float32)

    
    '''
    kernel = np.array([[-k, -k, -k],
                           [-k,  1+9*k, -k],
                           [-k, -k, -k]])
                           '''
    #sharpened = cv2.filter2D(frame, -1, kernel)

    return sharpened

"""
Preprocess a BGR image for Tesseract OCR.

Steps:
  1. BGR -> grayscale (if needed).
  2. Hard binarization with `ocr_bin_threshold` (cv2.THRESH_BINARY).
     The threshold must be chosen so that no inversion is required:
     the text should end up BLACK on WHITE background.
  3. Auto-upscale small images so the shorter side reaches at least
     `_OCR_TARGET_MIN_SIDE` px (capped at `_OCR_MAX_SCALE`), preserving
     aspect ratio. Larger images are left untouched.

Parameters
----------
img : np.ndarray
    Input image (BGR or already grayscale).
ocr_bin_threshold : int
    Threshold used for cv2.threshold(..., THRESH_BINARY).
debug : bool
    If True, returns (prep_img, debug_imgs) where debug_imgs is a dict
    with intermediate results: {"gray": ..., "bin": ...}. If False,
    returns prep_img only.

Returns
-------
prep_img : np.ndarray
    uint8 single-channel image ready for pytesseract.
debug_imgs : dict  (only when debug=True)
"""
_OCR_TARGET_MIN_SIDE = 100
_OCR_MAX_SCALE = 4.0

def OCR_imgPreprocess(img, ocr_bin_threshold, debug=False):
    if img is None or img.size == 0:
        raise ValueError("--ERR: OCR_imgPreprocess img is empty")
    if not isinstance(ocr_bin_threshold, (int, np.integer)):
        raise ValueError("--ERR: OCR_imgPreprocess ocr_bin_threshold must be int")
    ocr_bin_threshold = int(ocr_bin_threshold)
    if not (0 <= ocr_bin_threshold <= 255):
        raise ValueError("--ERR: OCR_imgPreprocess ocr_bin_threshold out of [0,255]")

    # 1) grayscale
    if img.ndim == 2:
        gray = img
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2) hard binarization (no inversion)
    _, bin_img = cv2.threshold(gray, ocr_bin_threshold, 255, cv2.THRESH_BINARY)

    # 3) auto-upscale small images
    h, w = bin_img.shape[:2]
    min_side = min(h, w)
    if min_side < _OCR_TARGET_MIN_SIDE:
        scale = min(_OCR_TARGET_MIN_SIDE / float(min_side), _OCR_MAX_SCALE)
        new_w = max(1, int(round(w * scale)))
        new_h = max(1, int(round(h * scale)))
        prep_img = cv2.resize(bin_img, (new_w, new_h),
                              interpolation=cv2.INTER_CUBIC)
    else:
        prep_img = bin_img

    if debug:
        return prep_img, {"gray": gray, "bin": bin_img}
    return prep_img