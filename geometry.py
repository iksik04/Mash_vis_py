"""
Shared 2D geometry helpers for rotated rectangles.

Conventions
-----------
- Angles are in RADIANS unless a function name says `_deg`.
- Coordinate system matches OpenCV: X right, Y down. A positive angle
  therefore looks clockwise on screen.
- A rotated rectangle is defined by its center (cx, cy), size (w, h) and
  rotation angle. Its corners are returned in the order TL, TR, BR, BL
  in the rectangle's local axes (TL has local coordinates (-w/2, -h/2)).
"""
import numpy as np

"""
2x2 rotation matrix. Angle in radians.
"""
def rot_matrix(angle_rad):
    ca, sa = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([[ca, -sa], [sa, ca]], dtype=np.float32)

"""
2x2 rotation matrix. Angle in degrees.
"""
def rot_matrix_deg(angle_deg):
    return rot_matrix(np.radians(angle_deg))

"""
4 corners (TL, TR, BR, BL) of a rotated rectangle.
"""
def rect_corners(cx, cy, w, h, angle_rad):
    half = np.array([[-w / 2, -h / 2],
                     [ w / 2, -h / 2],
                     [ w / 2,  h / 2],
                     [-w / 2,  h / 2]], dtype=np.float32)
    return half @ rot_matrix(angle_rad).T + np.array([cx, cy], dtype=np.float32)

"""
Midpoints of top, right, bottom, left sides (matching TL,TR,BR,BL).
"""
def side_midpoints(corners):
    return np.array([
        (corners[0] + corners[1]) / 2,  # top
        (corners[1] + corners[2]) / 2,  # right
        (corners[2] + corners[3]) / 2,  # bottom
        (corners[3] + corners[0]) / 2,  # left
    ], dtype=np.float32)

"""
Reconstruct the rectangle center from the world-space TL corner.

`x0, y0` is corners[0] (local TL) in world coordinates.
"""
def corner_to_center(x0, y0, w, h, angle_rad):
    local_tl = np.array([-w / 2, -h / 2], dtype=np.float32)
    c = np.array([x0, y0], dtype=np.float32) - rot_matrix(angle_rad) @ local_tl
    return float(c[0]), float(c[1])

"""
World-space TL corner from the rectangle center (inverse of above).
"""
def center_to_corner(cx, cy, w, h, angle_rad):
    local_tl = np.array([-w / 2, -h / 2], dtype=np.float32)
    p = rot_matrix(angle_rad) @ local_tl + np.array([cx, cy], dtype=np.float32)
    return float(p[0]), float(p[1])

"""
Normalize an angle into (-180, 180]. NaN passes through unchanged.
"""
def normalize_angle_deg(angle):
    if np.isnan(angle):
        return angle
    while angle <= -180:
        angle += 360
    while angle > 180:
        angle -= 360
    return angle