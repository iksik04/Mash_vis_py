"""
Interactive ROI selection with support for rotation, scaling, and moving.

Controls:
  - LMB on a corner          — resize
  - LMB on a side midpoint   — change rotation angle
  - LMB inside/on a side     — move
  - Enter / Space            — confirm
  - Esc                      — cancel
"""
from dataclasses import dataclass

import cv2
import numpy as np

import constants as c
from geometry import (
    rot_matrix,
    rect_corners,
    side_midpoints,
    corner_to_center,
    center_to_corner,
    normalize_angle_deg,
)
from roi import SingleROI

# --- tunables ---------------------------------------------------------------
_HANDLE_RADIUS = 10         # corner grab radius (px)
_ROT_HANDLE_RADIUS = 8      # rotation marker radius (px)
_MIN_SIZE = 10.0            # absolute minimum ROI side (px)
_WAIT_MS = 20


# ---------------------------------------------------------------------------
# Hit-testing
# ---------------------------------------------------------------------------
def _dist(p, q):
    return float(np.hypot(p[0] - q[0], p[1] - q[1]))

"""
Shrink the grab radius for tiny ROIs so all handles stay usable.
"""
def _effective_handle_radius(w, h):
    return float(min(_HANDLE_RADIUS, max(2.0, min(w, h) * 0.25)))

"""Classify the click.

Returns (kind, idx):
    'corner' — idx = 0..3
    'rotate' — idx = None
    'move'   — idx = None
    None     — miss
"""
def _hit_test(mouse, corners, mids, handle_radius):
    m = np.array(mouse, dtype=np.float32)

    # 1) corners have the highest priority
    for i, c in enumerate(corners):
        if _dist(m, c) <= handle_radius:
            return "corner", i

    # 2) rotation marker — midpoint of the top side
    rot_r = min(_ROT_HANDLE_RADIUS, handle_radius)
    if _dist(m, mids[0]) <= rot_r:
        return "rotate", None

    # 3) inside or on a side — move
    poly = corners.reshape(-1, 1, 2)
    if cv2.pointPolygonTest(poly, (float(m[0]), float(m[1])), False) >= 0:
        return "move", None

    return None, None


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------
def _draw(frame, corners, mids, handle_radius):
    cv2.polylines(frame, [np.round(corners).astype(np.int32)], True,
                  c.BLUE, c.ROI_LINE_WIDTH)
    for pt in np.round(corners).astype(np.int32):
        cv2.circle(frame, tuple(pt), int(round(handle_radius)), c.BLUE, c.ROI_LINE_WIDTH)
    cv2.circle(frame, tuple(np.round(mids[0]).astype(np.int32)),
               _ROT_HANDLE_RADIUS, c.BLUE, c.ROI_LINE_WIDTH)
    center = corners.mean(axis=0)
    cv2.drawMarker(frame,
                   (int(round(center[0])), int(round(center[1]))),
                   c.BLUE, cv2.MARKER_CROSS, 14, c.ROI_LINE_WIDTH)


# ---------------------------------------------------------------------------
# Interactive selection
# ---------------------------------------------------------------------------
"""Interactively select a rotated ROI.

Parameters
----------
window_name : str
    Window name; the window is created here if it does not exist yet.
frame : np.ndarray
    Frame on which the ROI is selected.
initial : (x0, y0, w, h, angle_deg) | None
    Initial ROI; `x0, y0` is the world-space TL corner. If None, the
ROI starts centered on the frame.

Returns
-------
(x0, y0, w, h, angle_deg) or None on Esc.
"""
def select_rotated_roi(window_name, frame, initial=None):
    if frame is None:
        raise ValueError("select_rotated_roi: frame is None")

    H, W = frame.shape[:2]

    if initial is not None:
        x0, y0, w, h, angle_deg = initial
        if w <= 0 or h <= 0:
            raise ValueError("select_rotated_roi: initial w/h must be positive")
        cx, cy = corner_to_center(x0, y0, w, h, np.radians(angle_deg))
    else:
        w = W / 4.0
        h = H / 4.0
        cx, cy = W / 2.0, H / 2.0
        angle_deg = 0.0

    state = {
        "cx": float(cx),
        "cy": float(cy),
        "w": float(w),
        "h": float(h),
        "angle": float(np.radians(angle_deg)),
        "drag": None,
        "drag_start": None,
        "drag_center": None,
        "drag_size": None,
        "drag_angle": None,
        "corner_sign": None,
    }

    def _snapshot_drag(kind, idx, x, y):
        state["drag"] = (kind, idx)
        state["drag_start"] = (float(x), float(y))
        state["drag_center"] = (state["cx"], state["cy"])
        state["drag_size"] = (state["w"], state["h"])
        state["drag_angle"] = state["angle"]
        if kind == "corner":
            signs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
            state["corner_sign"] = signs[idx]
        else:
            state["corner_sign"] = None

    def on_mouse(event, x, y, flags, param):
        corners = rect_corners(state["cx"], state["cy"],
                               state["w"], state["h"], state["angle"])
        mids = side_midpoints(corners)
        handle_r = _effective_handle_radius(state["w"], state["h"])

        if event == cv2.EVENT_LBUTTONDOWN:
            kind, idx = _hit_test((x, y), corners, mids, handle_r)
            if kind is None:
                return
            _snapshot_drag(kind, idx, x, y)

        elif event == cv2.EVENT_MOUSEMOVE and state["drag"] is not None:
            kind, _ = state["drag"]
            dx = x - state["drag_start"][0]
            dy = y - state["drag_start"][1]
            dcx, dcy = state["drag_center"]
            da = state["drag_angle"]
            R = rot_matrix(da)

            if kind == "move":
                state["cx"] = dcx + dx
                state["cy"] = dcy + dy

            elif kind == "rotate":
                new_angle = float(np.arctan2(y - dcy, x - dcx))
                state["angle"] = new_angle + np.pi / 2.0

            elif kind == "corner":
                sx, sy = state["corner_sign"]
                dw, dh = state["drag_size"]

                opp_local_old = np.array([-sx * dw / 2.0,
                                          -sy * dh / 2.0], dtype=np.float32)
                opp_world = np.array([dcx, dcy], dtype=np.float32) + R @ opp_local_old

                target_world = np.array([float(x), float(y)], dtype=np.float32)
                new_center = (opp_world + target_world) / 2.0

                diag_local = R.T @ (target_world - opp_world)
                state["cx"] = float(new_center[0])
                state["cy"] = float(new_center[1])
                state["w"] = max(abs(float(diag_local[0])), _MIN_SIZE)
                state["h"] = max(abs(float(diag_local[1])), _MIN_SIZE)

        elif event == cv2.EVENT_LBUTTONUP:
            state["drag"] = None
            state["corner_sign"] = None

    # Make sure the window exists before registering the callback.
    try:
        cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
    except cv2.error:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    cv2.setMouseCallback(window_name, on_mouse)

    try:
        while True:
            corners = rect_corners(state["cx"], state["cy"],
                                   state["w"], state["h"], state["angle"])
            mids = side_midpoints(corners)
            handle_r = _effective_handle_radius(state["w"], state["h"])

            vis = frame.copy()
            _draw(vis, corners, mids, handle_r)
            cv2.imshow(window_name, vis)

            key = cv2.waitKey(_WAIT_MS) & 0xFF
            if key in (10, 13, 32):  # Enter (both variants) / Space
                x0, y0 = center_to_corner(
                    state["cx"], state["cy"],
                    state["w"], state["h"],
                    state["angle"],
                )
                return (x0, y0,
                        float(state["w"]), float(state["h"]),
                        float(np.degrees(state["angle"])))
            if key == 27:  # Esc
                return None
    finally:
        cv2.setMouseCallback(window_name, lambda *a: None)


# ---------------------------------------------------------------------------
# Adapters to the project's ROI model
# ---------------------------------------------------------------------------
"""Select an ROI on `frame` and convert it to a `SingleROI`.

Parameters
----------
reference : RefImgContext
    Reference context; `reference.center` is the origin for `offset`.
name : str
    Unique ROI name.
delta_angle_deg : float
    Rotation of the *current* frame relative to the reference. Use 0 when
    selecting on the reference image itself.
initial : (x0, y0, w, h, angle_deg) | None
    Initial ROI expressed in the *current frame* (same format as
    `select_rotated_roi`). Use `None` for a fresh selection.
ocr_allowlist : passed through to SingleROI.
replace : reserved for the caller's container; not used here.

Returns
-------
SingleROI or None if cancelled.
"""
def select_single_roi(window_name, frame, reference, name,
                      delta_angle_deg=0.0, initial=None,
                      ocr_allowlist="", replace=False):
    if reference.center is None:
        raise ValueError("select_single_roi: reference.center is None; "
                         "call reference.build_ref_context() first")

    res = select_rotated_roi(window_name, frame, initial)
    if res is None:
        return None

    x0, y0, w, h, angle_deg = res

    # Absolute selection angle -> relative rotation angle.
    rotation_angle = normalize_angle_deg(angle_deg - delta_angle_deg)

    # World-space center of the selection, then offset from the reference
    # center, expressed back in the reference frame (undo delta_angle).
    cx, cy = corner_to_center(x0, y0, w, h, np.radians(angle_deg))
    inv_R = rot_matrix(np.radians(-delta_angle_deg))
    ref_cx, ref_cy = reference.center
    offset = inv_R @ (np.array([cx, cy], np.float32) - np.array([ref_cx, ref_cy], np.float32))

    return SingleROI(
        name=name,
        offset=(float(offset[0]), float(offset[1])),
        width=float(w),
        height=float(h),
        rotation_angle=float(rotation_angle),
        OCR_allowlist=ocr_allowlist,
    )

"""
cv2.selectROI-compatible wrapper returning the axis-aligned bbox.
"""
def select_roi_simple(window_name, frame, initial=None):
    res = select_rotated_roi(window_name, frame, initial)
    if res is None:
        return (0, 0, 0, 0)
    x0, y0, w, h, angle_deg = res
    corners = rect_corners(*corner_to_center(x0, y0, w, h, np.radians(angle_deg)),
                           w, h, np.radians(angle_deg))
    bx, by = corners[:, 0].min(), corners[:, 1].min()
    bw = corners[:, 0].max() - bx
    bh = corners[:, 1].max() - by
    return (int(round(bx)), int(round(by)),
            int(round(bw)), int(round(bh)))