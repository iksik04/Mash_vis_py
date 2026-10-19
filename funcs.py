import cv2
import numpy as np

import constants as c


def rgb2bin(img, low_threshold = c.BINARYSATION_LOW_THRESHOLD, high_threshold = c.BINARYSATION_HIGH_THRESHOLD):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary_img = cv2.threshold(gray_img, low_threshold, high_threshold, cv2.THRESH_BINARY)

    return binary_img

def external_countur_get(bin_img):
    contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = []
    for cnt in contours:
        length = cv2.arcLength(cnt, True)  # True = контур замкнут
        if length >= c.MIN_EXT_CONTOUR_LENGTH:
            filtered_contours.append(cnt)

    return filtered_contours

def draw_img(image, contour=None, rect=None, center=None, title="Image",
             contour_color=c.GREEN, contour_width=c.CONTOUR_LINE_WIDTH,
             rect_color=c.GREEN, rect_width=c.RECT_LINE_WIDTH,
             center_color=c.GREEN, center_size=None, center_width=c.CENTER_LINE_WIDTH
            ):
    
    # Приводим к BGR, если изображение в градациях серого
    if len(image.shape) == 2:
        canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        canvas = image.copy()

    if contour is not None:
        cv2.drawContours(canvas, contour, -1, contour_color, contour_width)

    if rect is not None:
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        cv2.drawContours(canvas, [box], 0, rect_color, rect_width)

    if center is not None:
        if center_size is None:
            if rect is not None:
                (_, _), (w, h), _ = rect
                center_size = int(min(w, h) / 20)
            else:
                center_size = 100

        cx, cy = int(center[0]), int(center[1])
        cv2.line(canvas, (cx - center_size, cy), (cx + center_size, cy),
                 center_color, center_width)
        cv2.line(canvas, (cx, cy - center_size), (cx, cy + center_size),
                 center_color, center_width)

    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.imshow(title, canvas)

def get_angle(img1, img2):
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
        print("Не удалось оценить преобразование")
    else:
        angle = np.degrees(np.arctan2(M[1, 0], M[0, 0]))
    return angle

# if __name__ == "__main__":
#    main()