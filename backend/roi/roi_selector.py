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

from .. import constants as c
from ..geometry import (
    rot_matrix,
    rect_corners,
    side_midpoints,
    corner_to_center,
    center_to_corner,
    normalize_angle_deg,
)
from .roi import SingleROI

# --- tunables ---------------------------------------------------------------
_HANDLE_RADIUS = 10         # corner grab radius (px)
_ROT_HANDLE_RADIUS = 8      # rotation marker radius (px)
_MIN_SIZE = 10.0            # absolute minimum ROI side (px)
_WAIT_MS = 20


# ---------------------------------------------------------------------------
# Hit-testing
# ---------------------------------------------------------------------------
"""
Euclidean distance between two 2D points.
"""
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
"""
Draw the ROI outline, corner handles, rotation marker and center cross.
"""
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
"""
Interactively select a rotated ROI.

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
        # --- zoom / pan ---
        # Display mapping: screen = world * zoom + pan.
        # `zoom_min = 1.0` guarantees the image is never shown smaller than
        # its original size, as required.
        "zoom": 1.0,
        "zoom_min": 1.0,
        "zoom_max": 10.0,
        "zoom_step": 1.1,
        "pan_x": 0.0,
        "pan_y": 0.0,
        "mouse_x": W // 2,
        "mouse_y": H // 2,
    }

    # --- coordinate transforms ------------------------------------------------
    # All ROI state is kept in world coordinates (pixels of `frame`).
    # Only screen coordinates differ, due to zoom and pan.

    def _to_world(sx, sy):
        """screen -> world (inverse of `screen = world*z + pan`)."""
        z = state["zoom"]
        return (sx - state["pan_x"]) / z, (sy - state["pan_y"]) / z

    def _to_screen(wx, wy):
        """world -> screen (`screen = world*z + pan`)."""
        z = state["zoom"]
        return wx * z + state["pan_x"], wy * z + state["pan_y"]

    def _affine_for_warp():
        """Affine matrix for `cv2.warpAffine` implementing the forward mapping
        `screen = world*z + pan`.

        `cv2.warpAffine` treats `M` as `dst -> src` by default, so we pass the
        forward matrix here and let OpenCV invert it internally. Passing an
        already-inverted matrix would result in a double inversion and make
        the image zoom out when `z > 1`.
        """
        z = state["zoom"]
        px, py = state["pan_x"], state["pan_y"]
        return np.float32([[z, 0.0, px],
                           [0.0, z, py]])

    # --- drag handling --------------------------------------------------------

    def _snapshot_drag(kind, idx, wx, wy):
        """Capture the state needed to process a drag started at world point
        `(wx, wy)` for a handle of type `kind`."""
        state["drag"] = (kind, idx)
        state["drag_start"] = (float(wx), float(wy))
        state["drag_center"] = (state["cx"], state["cy"])
        state["drag_size"] = (state["w"], state["h"])
        state["drag_angle"] = state["angle"]
        if kind == "corner":
            # Local-space diagonal signs for corners 0..3 (TL, TR, BR, BL).
            signs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
            state["corner_sign"] = signs[idx]
        else:
            state["corner_sign"] = None

    def on_mouse(event, x, y, flags, param):
        # Remember the last screen-space cursor position so the wheel handler
        # can fall back to it if the backend sends (-1, -1) in the event.
        if event in (cv2.EVENT_MOUSEMOVE, cv2.EVENT_LBUTTONDOWN,
                     cv2.EVENT_LBUTTONUP, cv2.EVENT_MOUSEWHEEL):
            state["mouse_x"] = x
            state["mouse_y"] = y

        # Convert cursor to world coordinates; everything below works in world.
        wx, wy = _to_world(x, y)

        corners = rect_corners(state["cx"], state["cy"],
                               state["w"], state["h"], state["angle"])
        mids = side_midpoints(corners)
        handle_r = _effective_handle_radius(state["w"], state["h"])

        if event == cv2.EVENT_LBUTTONDOWN:
            kind, idx = _hit_test((wx, wy), corners, mids, handle_r)
            if kind is None:
                return
            _snapshot_drag(kind, idx, wx, wy)

        elif event == cv2.EVENT_MOUSEMOVE and state["drag"] is not None:
            kind, _ = state["drag"]
            dx = wx - state["drag_start"][0]
            dy = wy - state["drag_start"][1]
            dcx, dcy = state["drag_center"]
            da = state["drag_angle"]
            R = rot_matrix(da)

            if kind == "move":
                state["cx"] = dcx + dx
                state["cy"] = dcy + dy

            elif kind == "rotate":
                new_angle = float(np.arctan2(wy - dcy, wx - dcx))
                state["angle"] = new_angle + np.pi / 2.0

            elif kind == "corner":
                sx, sy = state["corner_sign"]
                dw, dh = state["drag_size"]

                # Keep the opposite corner fixed while dragging the grabbed one.
                opp_local_old = np.array([-sx * dw / 2.0,
                                          -sy * dh / 2.0], dtype=np.float32)
                opp_world = np.array([dcx, dcy], dtype=np.float32) + R @ opp_local_old

                target_world = np.array([float(wx), float(wy)], dtype=np.float32)
                new_center = (opp_world + target_world) / 2.0

                diag_local = R.T @ (target_world - opp_world)
                state["cx"] = float(new_center[0])
                state["cy"] = float(new_center[1])
                state["w"] = max(abs(float(diag_local[0])), _MIN_SIZE)
                state["h"] = max(abs(float(diag_local[1])), _MIN_SIZE)

        elif event == cv2.EVENT_LBUTTONUP:
            state["drag"] = None
            state["corner_sign"] = None

        elif event == cv2.EVENT_MOUSEWHEEL:
            # The direction is encoded in the high word of `flags` as a signed
            # 16-bit value. Checking `flags > 0` directly is fragile because
            # modifier keys also set bits in `flags`.
            delta = (flags >> 16) & 0xFFFF
            if delta >= 0x8000:
                delta -= 0x10000
            if delta == 0:
                return

            factor = state["zoom_step"] if delta > 0 else 1.0 / state["zoom_step"]
            old_z = state["zoom"]
            new_z = max(state["zoom_min"], min(state["zoom_max"], old_z * factor))

            # Nothing to do if we are already at a boundary and the frame is
            # in its original position.
            if new_z == old_z and state["pan_x"] == 0.0 and state["pan_y"] == 0.0:
                return

            # Zoom towards the cursor. Use the last known cursor position if
            # the backend reports invalid coordinates in this event.
            mx, my = x, y
            if mx < 0 or my < 0:
                mx, my = state["mouse_x"], state["mouse_y"]

            # World point currently under the cursor (with the old zoom/pan).
            wx_c, wy_c = _to_world(mx, my)

            # Recompute pan so that the same world point stays under the
            # cursor after the zoom change: mx = wx_c * new_z + pan_x_new.
            state["zoom"] = new_z
            state["pan_x"] = mx - wx_c * new_z
            state["pan_y"] = my - wy_c * new_z

            # When fully zoomed out, reset the pan so the frame returns to
            # its original position.
            if new_z == 1.0:
                state["pan_x"] = 0.0
                state["pan_y"] = 0.0

    # Make sure the window exists before registering the callback.
    try:
        cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
    except cv2.error:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    cv2.setMouseCallback(window_name, on_mouse)

    try:
        while True:
            z = state["zoom"]
            px, py = state["pan_x"], state["pan_y"]

            # Render the frame with the current zoom/pan. The output size is
            # fixed to the original frame size so the window does not resize;
            # areas outside the source frame are filled with black.
            if z == 1.0 and px == 0.0 and py == 0.0:
                disp = frame.copy()
            else:
                disp = cv2.warpAffine(
                    frame, _affine_for_warp(), (W, H),
                    flags=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT,
                    borderValue=(0, 0, 0),
                )

            # Draw the ROI in screen coordinates using the same transform as
            # the image, so it always aligns with the underlying pixels.
            corners = rect_corners(state["cx"], state["cy"],
                                   state["w"], state["h"], state["angle"])
            mids = side_midpoints(corners)
            handle_r = _effective_handle_radius(state["w"], state["h"])

            corners_draw = np.array(
                [_to_screen(cx_, cy_) for cx_, cy_ in corners],
                dtype=np.float32,
            )
            mids_draw = np.array(
                [_to_screen(mx_, my_) for mx_, my_ in mids],
                dtype=np.float32,
            )
            handle_r_draw = max(3.0, handle_r * z)

            _draw(disp, corners_draw, mids_draw, handle_r_draw)
            cv2.imshow(window_name, disp)

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