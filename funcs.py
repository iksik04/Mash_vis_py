import cv2
import numpy as np

import constants as c

# turns rgb image into binary
def rgb2bin(img, low_threshold = c.BINARYSATION_LOW_THRESHOLD, high_threshold = c.BINARYSATION_HIGH_THRESHOLD):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary_img = cv2.threshold(gray_img, low_threshold, high_threshold, cv2.THRESH_BINARY)

    return binary_img

# gets the longest contour from binary image
def external_countur_get(bin_img):
    contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = []
    for cnt in contours:
        length = cv2.arcLength(cnt, True)
        if length >= c.MIN_EXT_CONTOUR_LENGTH:
            filtered_contours.append(cnt)
    return filtered_contours

# draws image. Countur, rectangle and center are optional
def draw_img(image, contour=None, rectangle=False, center=False, title="Image",
             contour_color=c.GREEN, contour_width=c.CONTOUR_LINE_WIDTH,
             rect_color=c.GREEN, rect_width=c.RECT_LINE_WIDTH,
             center_color=c.GREEN, center_size=None, center_width=c.CENTER_LINE_WIDTH
            ):

    if len(contour) == 0: contour = None

    if len(image.shape) == 2:
        canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        canvas = image.copy()

    if contour is not None:
        cv2.drawContours(canvas, contour, -1, contour_color, contour_width)
    else:
        rectangle = False
        center = False

    if rectangle:
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        cv2.drawContours(canvas, [box], 0, rect_color, rect_width)

    if center:
        if not rectangle: rect = cv2.minAreaRect(contour)
        (cx, cy), (w, h), angle = rect
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
    cv2.imshow(title, canvas)

# gets angle between two images
def get_angle(img1, img2, prev_angle=None):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    matches = matches[:50]

    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    M, _ = cv2.estimateAffinePartial2D(src_pts, dst_pts)
    if M is None:
        print("--ERR: AffinePartial2D")
        return prev_angle if prev_angle is not None else 0.0
    
    angle = np.degrees(np.arctan2(M[1, 0], M[0, 0]))

    if prev_angle is not None:
        while angle - prev_angle > 180.0:
            angle -= 360.0
        while angle - prev_angle < -180.0:
            angle += 360.0
    return angle

# calculates new ROI corners coordinates with offset and rotation 
def get_roi_corners(roi_offset, roi_w, roi_h, cur_center, d_angle):
    rad = np.radians(d_angle)
    cos_a, sin_a = np.cos(rad), np.sin(rad)

    ox, oy = roi_offset
    rot_ox = ox * cos_a - oy * sin_a
    rot_oy = ox * sin_a + oy * cos_a
    roi_cx = cur_center[0] + rot_ox
    roi_cy = cur_center[1] + rot_oy

    half_w, half_h = roi_w / 2.0, roi_h / 2.0
    corners = np.array([
        [-half_w, -half_h],
        [ half_w, -half_h],
        [ half_w,  half_h],
        [-half_w,  half_h],
    ], dtype=np.float32)
    rotated = corners @ np.array([[cos_a, sin_a], [-sin_a, cos_a]], dtype=np.float32)
    rotated[:, 0] += roi_cx
    rotated[:, 1] += roi_cy
    return np.intp(rotated)

# if __name__ == "__main__":
#    main()