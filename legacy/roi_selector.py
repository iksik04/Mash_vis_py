'''
Interactive ROI selection with support for rotation, scaling, and moving.

Controls:
  - LMB on a corner          — resize
  - LMB on a side point      — change rotation angle
  - LMB inside/on a side     — move
  - Enter / Space            — confirm
  - Esc                      — cancel
'''
import numpy as np
import cv2

import legacy.constants as c

# handle grab radius (px)
_HANDLE_RADIUS = 10
# rotation marker radius (px)
_ROT_HANDLE_RADIUS = 8
# minimum ROI size when scaling
_MIN_SIZE = 10.0


def _rot(angle_rad: float) -> np.ndarray:
    ca, sa = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([[ca, -sa], [sa, ca]], dtype=np.float32)

'''
Returns the 4 ROI corners in order: TL, TR, BR, BL (in local axes).
'''
def _corners_from(cx, cy, w, h, angle_rad):
    half = np.array([[-w / 2, -h / 2],
                     [ w / 2, -h / 2],
                     [ w / 2,  h / 2],
                     [-w / 2,  h / 2]], dtype=np.float32)
    R = _rot(angle_rad)
    return half @ R.T + np.array([cx, cy], dtype=np.float32)

'''
Side midpoints: top, right, bottom, left (in the order of corners TL,TR,BR,BL).
'''
def _side_midpoints(corners):
    return np.array([
        (corners[0] + corners[1]) / 2,  # top
        (corners[1] + corners[2]) / 2,  # right
        (corners[2] + corners[3]) / 2,  # bottom
        (corners[3] + corners[0]) / 2,  # left
    ], dtype=np.float32)


def _dist(p, q):
    return float(np.hypot(p[0] - q[0], p[1] - q[1]))

'''
Returns:
    ('corner', i)  — if the i-th corner was hit
    ('rotate', None)— if the rotation marker was hit (midpoint of the top side)
    ('move', None)  — if inside or on a side
    (None, None)    — if missed
'''
def _hit_test(mouse, corners, mids):
    m = np.array(mouse, dtype=np.float32)

    # 1) corners (higher priority than rotation)
    for i, c in enumerate(corners):
        if _dist(m, c) <= _HANDLE_RADIUS:
            return 'corner', i

    # 2) rotation marker — midpoint of the top side
    if _dist(m, mids[0]) <= _ROT_HANDLE_RADIUS:
        return 'rotate', None

    # 3) inside or on a side — move
    #    use pointPolygonTest: >= 0 means inside or on the boundary
    poly = corners.astype(np.float32).reshape(-1, 1, 2)
    if cv2.pointPolygonTest(poly, (float(m[0]), float(m[1])), False) >= 0:
        return 'move', None

    return None, None


def _draw(frame, corners, mids, angle_deg):
    poly = corners  # float32, no intp
    cv2.polylines(frame, [np.round(poly).astype(np.int32)], True,
                  c.BLUE, c.ROI_LINE_WIDTH)
    for pt in np.round(corners).astype(np.int32):
        cv2.circle(frame, tuple(pt), _HANDLE_RADIUS, c.BLUE, c.ROI_LINE_WIDTH)
    rm = tuple(np.round(mids[0]).astype(np.int32))
    cv2.circle(frame, rm, _ROT_HANDLE_RADIUS, c.BLUE, c.ROI_LINE_WIDTH)
    center = corners.mean(axis=0)
    cv2.drawMarker(frame, (int(round(center[0])), int(round(center[1]))),
                   c.BLUE, cv2.MARKER_CROSS, 14, c.ROI_LINE_WIDTH)


'''
Interactive selection of a rotated ROI.

Parameters
----------
window_name : str
    Window name (must be created beforehand via cv2.namedWindow).
frame : np.ndarray
    Frame on which the ROI is selected.
initial : tuple | None
    (x0, y0, w, h, angle_deg) — initial ROI position.
If None — the ROI is created at the center of the frame with size 1/4.

Returns
-------
(x0, y0, w, h, angle_deg) or None if the selection is canceled (Esc).
    x0, y0 — coordinates of the ROI *corner* (top-left corner in local axes,
                taking rotation into account — that is, corners[0]).
     w, h    — ROI dimensions.
    angle_deg — rotation angle in degrees.
'''
def select_rotated_roi(window_name: str, frame,
                       initial=None) -> tuple[float, float, float, float, float] | None:
    H, W = frame.shape[:2]

    if initial is not None:
        x0, y0, w, h, angle_deg = initial
        # reconstruct the center from the "corner" (the corner is corners[0] in local axes)
        angle_rad = np.radians(angle_deg)
        local_tl = np.array([-w / 2, -h / 2], dtype=np.float32)
        R = _rot(angle_rad)
        center = np.array([x0, y0], dtype=np.float32) - R @ local_tl
        cx, cy = float(center[0]), float(center[1])
    else:
        w = W / 4.0
        h = H / 4.0
        cx, cy = W / 2.0, H / 2.0
        angle_rad = 0.0
        angle_deg = 0.0

    state = {
        'cx': cx, 'cy': cy,
        'w': float(w), 'h': float(h),
        'angle': float(angle_rad),
        'drag': None,          # ('corner', i) | ('rotate', None) | ('move', None)
        'drag_start': None,    # (mouse_x, mouse_y)
        'drag_center': None,   # (cx, cy) at the start of the drag
        'drag_size': None,     # (w, h)
        'drag_angle': None,    # angle_rad
        'corner_sign': None,   # (sx, sy) — local signs of the corner
    }

    def on_mouse(event, x, y, flags, param):
        corners = _corners_from(state['cx'], state['cy'],
                                state['w'], state['h'], state['angle'])
        mids = _side_midpoints(corners)

        if event == cv2.EVENT_LBUTTONDOWN:
            kind, idx = _hit_test((x, y), corners, mids)
            if kind is None:
                return
            state['drag'] = (kind, idx)
            state['drag_start'] = (float(x), float(y))
            state['drag_center'] = (state['cx'], state['cy'])
            state['drag_size'] = (state['w'], state['h'])
            state['drag_angle'] = state['angle']
            if kind == 'corner':
                # local signs of the corner: TL(-,-), TR(+,-), BR(+,+), BL(-,+)
                signs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
                state['corner_sign'] = signs[idx]

        elif event == cv2.EVENT_MOUSEMOVE and state['drag'] is not None:
            kind, idx = state['drag']
            dx = x - state['drag_start'][0]
            dy = y - state['drag_start'][1]
            dcx, dcy = state['drag_center']
            dw, dh = state['drag_size']
            da = state['drag_angle']
            R = _rot(da)

            if kind == 'move':
                state['cx'] = dcx + dx
                state['cy'] = dcy + dy

            elif kind == 'rotate':
                # angle from the center to the mouse
                new_angle = float(np.arctan2(y - dcy, x - dcx))
                # the rotation marker was on the top side => -pi/2 from the center
                state['angle'] = new_angle + np.pi / 2.0

            elif kind == 'corner':
                sx, sy = state['corner_sign']
                dcx, dcy = state['drag_center']
                dw, dh = state['drag_size']
                da = state['drag_angle']
                R = _rot(da)

                # 1) opposite corner in world space (does not change)
                opp_local_old = np.array([-sx * dw / 2.0,
                                        -sy * dh / 2.0], dtype=np.float32)
                opp_world = np.array([dcx, dcy], dtype=np.float32) + R @ opp_local_old

                # 2) where the cursor came to — that is where the dragged corner should go
                target_world = np.array([float(x), float(y)], dtype=np.float32)

                # 3) new center = midpoint of the diagonal
                new_center = (opp_world + target_world) / 2.0

                # 4) new dimensions — projection of the diagonal onto the local axes
                diag_local = R.T @ (target_world - opp_world)
                new_w = max(abs(float(diag_local[0])), _MIN_SIZE)
                new_h = max(abs(float(diag_local[1])), _MIN_SIZE)

                state['cx'] = float(new_center[0])
                state['cy'] = float(new_center[1])
                state['w'] = new_w
                state['h'] = new_h

        elif event == cv2.EVENT_LBUTTONUP:
            state['drag'] = None

    cv2.setMouseCallback(window_name, on_mouse)

    while True:
        corners = _corners_from(state['cx'], state['cy'],
                                state['w'], state['h'], state['angle'])
        mids = _side_midpoints(corners)

        vis = frame.copy()
        _draw(vis, corners, mids, np.degrees(state['angle']))
        cv2.imshow(window_name, vis)

        key = cv2.waitKey(20) & 0xFF
        if key in (13, 32):  # Enter / Space
            cv2.setMouseCallback(window_name, lambda *a: None)
            corners = _corners_from(state['cx'], state['cy'],
                                    state['w'], state['h'], state['angle'])
            x0, y0 = corners[0]  # TL in local axes
            return (float(x0), float(y0),
                    float(state['w']), float(state['h']),
                    float(np.degrees(state['angle'])))
        elif key == 27:  # Esc
            cv2.setMouseCallback(window_name, lambda *a: None)
            return None

'''
Wrapper around select_rotated_roi that returns (x0, y0, w, h) without the angle —
compatible with the cv2.selectROI format.
'''
def select_roi_simple(window_name: str, frame, initial=None):
    res = select_rotated_roi(window_name, frame, initial)
    if res is None:
        return (0, 0, 0, 0)
    x0, y0, w, h, _ = res
    return (int(round(x0)), int(round(y0)),
            int(round(w)), int(round(h)))