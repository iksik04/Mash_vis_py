"""
Render the result of `validation.validate` on top of the source frame.

Public API
----------
render_validation(frame, result, multi_roi) -> np.ndarray
    Returns a BGR copy of `frame` with:
      - the detected outer contour, coloured by `result.ext_contour_ok`
        (GREEN ok / RED ng / YELLOW skip);
      - every ROI outline + name label, coloured by `result.rois[name]`;
      - the main ROI contour (if found), transformed from the ROI patch
        back into world coordinates and drawn in the same colour;
      - the recognized OCR text (or "no text") in the ROI's bottom-left
        corner, coloured likewise, with font size auto-shrunk to fit the
        ROI width.

The function never calls cv2.imshow / waitKey; callers decide how to
display the returned image.
"""
import cv2
import numpy as np

from .. import constants as c
from ..geometry import rot_matrix_deg


# --- helpers ---------------------------------------------------------------

"""
Map a status bool|None to a colour.
"""
def _status_color(value):
    if value is True:
        return c.GREEN
    if value is False:
        return c.RED
    return c.YELLOW


"""
Transform ROI-local contour points (patch pixel coords) to world coords.

`corners_at` returns (corners, roi_center, R_roi), so we reuse them to get
the exact same rotation/center as when the ROI was extracted.
"""
def _roi_local_to_world(contour, roi, ref_center, delta_angle):
    if contour is None or len(contour) == 0:
        return None
    _, roi_center, R_roi = roi.corners_at(ref_center, delta_angle)
    pts = contour.reshape(-1, 2).astype(np.float32)        # (N, 2) in patch coords
    w = roi.width
    h = roi.height
    # extract() maps world -> patch as: p_patch = R^T * (p_world - c) + (w/2, h/2)
    # inverse:                            p_world = R * (p_patch - (w/2, h/2)) + c
    local = pts - np.array([w / 2.0, h / 2.0], np.float32)
    world = local @ R_roi.T + roi_center
    return world.reshape(-1, 1, 2).astype(np.int32)


"""
Draw `text` in the top-left corner of the ROI quad, shrinking the font
until it fits the ROI's top-side length. Fallback: truncate with '…'.
"""
def _draw_fitted_text(img, text, anchor, max_width, color, thickness=1,
                      max_scale=1.2, min_scale=0.3):
    if not text:
        return
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = max_scale
    while scale > min_scale:
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        if tw <= max_width:
            break
        scale -= 0.05
    # final measurement; if still too wide, truncate
    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
    if tw > max_width:
        # reserve room for the ellipsis
        dots = "..."
        (dw, _), _ = cv2.getTextSize(dots, font, scale, thickness)
        avail = max_width - dw
        cut = text
        while cut and cv2.getTextSize(cut, font, scale, thickness)[0][0] > avail:
            cut = cut[:-1]
        text = cut + dots
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)

    # anchor is the bottom-left of the text baseline
    x, y = int(round(anchor[0])), int(round(anchor[1]))
    # keep on screen
    x = max(0, x)
    y = max(th + 1, min(img.shape[0] - 1, y))
    cv2.putText(img, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)


# --- public API ------------------------------------------------------------

"""
Render `result` (from validation.validate) on a copy of `frame`.

Parameters
----------
frame : np.ndarray
    The same frame that was passed to validate().
result : ValidationResult
    Must contain the visualisation fields (cur_center, delta_angle,
    cur_ext_contour, roi_contours, roi_texts, ...).
multi_roi : MultiROI
    The container used for validation; supplies ROI geometry and names.

Returns
-------
np.ndarray
    BGR copy of `frame` with the overlay.
"""
def render_validation(frame, result, multi_roi):
    if frame is None:
        raise ValueError("--ERR: render_validation frame is None")
    if result is None:
        raise ValueError("--ERR: render_validation result is None")
    if multi_roi is None:
        raise ValueError("--ERR: render_validation multi_roi is None")

    canvas = frame.copy()
    if canvas.ndim == 2:
        canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)

    # --- outer contour -------------------------------------------------
    ext_color = _status_color(result.ext_contour_ok)
    if result.cur_ext_contour is not None:
        cv2.drawContours(canvas, [result.cur_ext_contour], -1,
                         ext_color, c.CONTOUR_LINE_WIDTH)

    # --- per-ROI overlays ----------------------------------------------
    ref_center = result.cur_center
    delta_angle = result.delta_angle if result.delta_angle is not None else 0.0

    # Nothing to draw if the current geometry is unknown (ext_contour failed early).
    if ref_center is None:
        return canvas

    for name, roi in multi_roi.rois.items():
        status = result.rois.get(name)          # missing -> None -> YELLOW
        color = _status_color(status)

        # outline + name label (SingleROI.render already draws both)
        roi.render(canvas, ref_center=ref_center, delta_angle=delta_angle,
                   color=color, width=c.ROI_LINE_WIDTH)
        # SingleROI.render paints the label GREEN unconditionally; re-paint
        # it in the status colour to keep the visual consistent.
        corners, _, _ = roi.corners_at(ref_center, delta_angle)
        tl = tuple(map(int, corners[0]))
        cv2.putText(canvas, name, tl, cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, color, 2, cv2.LINE_AA)

        # main ROI contour, transformed back to world coords
        world_cnt = _roi_local_to_world(
            result.roi_contours.get(name), roi, ref_center, delta_angle
        )
        if world_cnt is not None:
            cv2.drawContours(canvas, [world_cnt], -1, color,
                             c.CONTOUR_LINE_WIDTH)

        # OCR text in the ROI's bottom-left corner
        text = result.roi_texts.get(name, "")
        if text == "":
            text = "no text"
        # bottom-left corner of the ROI (local BL)
        bl = tuple(map(int, corners[3]))
        # top-side length = width available for the text
        top_len = float(np.linalg.norm(corners[1] - corners[0]))
        # baseline slightly above the bottom edge
        anchor = (bl[0], bl[1] - 4)
        _draw_fitted_text(canvas, text, anchor,
                          max_width=max(10.0, top_len - 4.0),
                          color=color,
                          thickness=1,
                          max_scale=1.2,
                          min_scale=0.3)

    return canvas