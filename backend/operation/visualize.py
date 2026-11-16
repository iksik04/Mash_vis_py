"""
Render the result of `validation.validate`.

Public API
----------
render_ng_roi(roi_patch, result, name) -> np.ndarray
    BGR image of one failed ROI: grayscale background, RED main contour
    (only if the ROI failed the contour stage) and/or RED recognized text
    in the bottom-left corner (only if the ROI failed the symbols stage).

render_validation_result(frame, result, multi_roi) -> dict[str, np.ndarray]
    Returns a dict of rendered images:
      - "main"          : full frame, grayscale background, coloured ROI
                          outlines/labels and the outer contour;
      - f"fail:{name}"  : one entry per NG ROI (produced by render_ng_roi).

show_validation_result(images) -> None
    Displays every image from `images` at once, waits for a key press,
    then closes the windows. Windows are named after the dict keys
    ("main" -> "Validation"; "fail:<name>" -> "Validation fail: <stage>, <name>").
"""
import cv2
import numpy as np

from .. import constants as c


# --- helpers ---------------------------------------------------------------

def _status_color(value):
    if value is True:
        return c.GREEN
    if value is False:
        return c.RED
    return c.YELLOW


def _to_gray_bgr(img):
    """Return a BGR image whose background is the grayscale version of `img`."""
    if img.ndim == 2:
        gray = img
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def _resize_to_fit(img, target_w=500, max_h=None):
    """Scale `img` so that width == target_w, unless that makes the height
    exceed `max_h`; in that case the height is clamped to `max_h` and the
    width shrinks proportionally (aspect preserved, INTER_AREA on shrink)."""
    h, w = img.shape[:2]
    if w == 0 or h == 0:
        return img
    scale = target_w / float(w)
    if max_h is not None and h * scale > max_h:
        scale = max_h / float(h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
    return cv2.resize(img, (new_w, new_h), interpolation=interp)


def _stage_label(result, name):
    """Stage string for the window title"""
    cont = bool(result.roi_contour_failed.get(name, False))
    sym  = bool(result.roi_symbols_failed.get(name, False))
    if cont and sym:
        return "roi_contours+roi_symbols"
    if cont:
        return "roi_contours"
    if sym:
        return "roi_symbols"
    return result.stage or "unknown"


def _draw_fitted_text(img, text, anchor, max_width, max_height, color,
                      thickness=1, max_scale=1.2, min_scale=0.3):
    """Draw `text` with font auto-shrunk to fit both `max_width` and
    `max_height`; truncate with '...' as a last resort.
    `anchor` is the bottom-left of the baseline."""
    if not text:
        return
    font = cv2.FONT_HERSHEY_SIMPLEX
    # don't let the font grow larger than ~1/3 of the available height
    if max_height is not None and max_height > 0:
        max_scale = min(max_scale, max_height / 30.0)

    scale = max_scale
    while scale > min_scale:
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        if tw <= max_width and (max_height is None or th <= max_height):
            break
        scale -= 0.05
    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
    if tw > max_width:
        dots = "..."
        (dw, _), _ = cv2.getTextSize(dots, font, scale, thickness)
        avail = max_width - dw
        cut = text
        while cut and cv2.getTextSize(cut, font, scale, thickness)[0][0] > avail:
            cut = cut[:-1]
        text = cut + dots
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)

    x = max(0, int(round(anchor[0])))
    y = max(th + 1, min(img.shape[0] - 1, int(round(anchor[1]))))
    cv2.putText(img, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)


# --- public API ------------------------------------------------------------

"""
Render one failed ROI on a grayscale background.

Parameters
----------
roi_patch : np.ndarray
    The ROI patch (BGR or grayscale) as extracted from the current frame.
result : ValidationResult
    Must contain roi_contours / roi_texts / roi_contour_failed /
    roi_symbols_failed for `name`.
name : str
    ROI name.

Returns
-------
np.ndarray
    BGR image sized as `roi_patch`, grayscale background, RED overlay
    only for the stages the ROI failed on.
"""
def render_ng_roi(roi_patch, result, name):
    if roi_patch is None or roi_patch.size == 0:
        raise ValueError(f"--ERR: render_ng_roi roi_patch is empty for '{name}'")

    canvas = _to_gray_bgr(roi_patch)
    h, w = canvas.shape[:2]

    cont_failed = bool(result.roi_contour_failed.get(name, False))
    sym_failed  = bool(result.roi_symbols_failed.get(name, False))

    # main ROI contour (patch-local coords) — only if the ROI failed contours
    if cont_failed:
        cnt = result.roi_contours.get(name)
        if cnt is not None and len(cnt) > 0:
            cv2.drawContours(canvas, [cnt.reshape(-1, 1, 2).astype(np.int32)],
                             -1, c.RED, c.CONTOUR_LINE_WIDTH)

    # OCR text — only if the ROI failed symbols
    if sym_failed:
        text = result.roi_texts.get(name, "")
        if not text:
            text = "no text"
        anchor = (2, h - 4)
        _draw_fitted_text(canvas, text, anchor,
                          max_width=max(10.0, float(w) - 4.0),
                          max_height=float(h) - 8.0,
                          color=c.RED, thickness=1,
                          max_scale=1.2, min_scale=0.3)

    return canvas


"""
Render the full validation result.

Parameters
----------
frame : np.ndarray
    The frame that was passed to validate().
result : ValidationResult
    Output of validate().
multi_roi : MultiROI
    The container used for validation.

Returns
-------
dict[str, np.ndarray]
    {
        "main":           <full frame overlay>,
        "fail:<name>":    <NG ROI image>,   # one per failed ROI
        ...
    }
"""
def render_validation_result(frame, result, multi_roi):
    if frame is None:
        raise ValueError("--ERR: render_validation_result frame is None")
    if result is None:
        raise ValueError("--ERR: render_validation_result result is None")
    if multi_roi is None:
        raise ValueError("--ERR: render_validation_result multi_roi is None")

    # --- main canvas: grayscale background --------------------------------
    canvas = _to_gray_bgr(frame)

    # outer contour (colour by ext_contour_ok)
    ext_color = _status_color(result.ext_contour_ok)
    if result.cur_ext_contour is not None:
        cv2.drawContours(canvas, [result.cur_ext_contour], -1,
                         ext_color, c.CONTOUR_LINE_WIDTH)

    ref_center = result.cur_center
    delta_angle = result.delta_angle if result.delta_angle is not None else 0.0

    # If the outer contour failed, ROIs are not validated -> nothing to draw.
    out = {"main": canvas}
    if result.ext_contour_ok is not True:
        return out

    # --- ROI outlines + labels -------------------------------------------
    for name, roi in multi_roi.rois.items():
        color = _status_color(result.rois.get(name))
        corners, roi_center, _ = roi.corners_at(ref_center, delta_angle)

        cv2.polylines(canvas, [corners.reshape(-1, 1, 2)], True,
                      color, c.ROI_LINE_WIDTH)
        cv2.drawMarker(canvas, tuple(map(int, roi_center)),
                       color, cv2.MARKER_CROSS, 12, c.ROI_LINE_WIDTH)
        cv2.putText(canvas, name, tuple(map(int, corners[0])),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

    # --- failed ROI images ------------------------------------------------
    patches = multi_roi.extract_all(frame=frame,
                                    ref_center=ref_center,
                                    delta_angle=delta_angle)
    for name, status in result.rois.items():
        if status is not False:
            continue
        patch = patches.get(name)
        if patch is None or patch.size == 0:
            continue
        out[f"fail:{name}"] = render_ng_roi(patch, result, name)

    return out


"""
Display every image from `images` at once, wait for a key press and close.

Window titles
-------------
    "main"         -> "Validation"
    "fail:<name>"  -> f"Validation fail: {stage}, {name}"
                     where `stage` is derived from result.roi_contour_failed /
                     result.roi_symbols_failed via `_stage_label`.
"""
def show_validation_result(images, result=None):
    if not images:
        return
    windows = []
    try:
        for key, img in images.items():
            if key == "main":
                title = "Validation"
                disp = img
            elif key.startswith("fail:") and result is not None:
                name = key[len("fail:"):]
                stage = _stage_label(result, name)
                title = f"Validation fail: {stage}, {name}"
                disp = _resize_to_fit(img, target_w=500,
                                      max_h=c.CAM_HEIGHT)
            else:
                title = key
                disp = img
            cv2.imshow(title, disp)
            windows.append(title)
        cv2.waitKey(0)
    finally:
        for title in windows:
            try:
                cv2.destroyWindow(title)
            except cv2.error:
                pass