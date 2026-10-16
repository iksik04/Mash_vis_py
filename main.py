MIN_EXT_CONTOUR_LENGTH = 50  # минимальная длина периметра контура в пикселях

# Line width
CONTOUR_LINE_WIDTH = 8
RECT_LINE_WIDTH = 8
CENTER_LINE_WIDTH = 8

# Colours
GREEN = (0, 255, 0)
# Thresholds
EXT_COUNTUR_MATCH_THRESHOLD = 0.01

ref_image_path = "im1.jpg"
test_image_path = "im2.jpg"

import cv2
import numpy as np

def rgb2bin(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary_img = cv2.threshold(gray_img, 40, 255, cv2.THRESH_BINARY)

    return binary_img

def external_countur_get(bin_img):
    contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = []
    for cnt in contours:
        length = cv2.arcLength(cnt, True)  # True = контур замкнут
        if length >= MIN_EXT_CONTOUR_LENGTH:
            filtered_contours.append(cnt)

    return filtered_contours[0]

def draw_img(image, contour=None, rect=None, center=None, title="Image",
             contour_color=GREEN, contour_width=CONTOUR_LINE_WIDTH,
             rect_color=GREEN, rect_width=RECT_LINE_WIDTH,
             center_color=GREEN, center_size=None, center_width=CENTER_LINE_WIDTH
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


def main():

    ref_img = cv2.imread(ref_image_path)
    test_img = cv2.imread(test_image_path)

    ref_bin_img = rgb2bin(ref_img)
    test_bin_img = rgb2bin(test_img)

    ref_ext_countour = external_countur_get(ref_bin_img)
    test_ext_countour = external_countur_get(test_bin_img)

    match_value = cv2.matchShapes(ref_ext_countour, test_ext_countour, cv2.CONTOURS_MATCH_I1, 0.0)

    if match_value >= EXT_COUNTUR_MATCH_THRESHOLD:
        print("EXT_COUNTUR_MATCH_THRESHOLD --NG")
    else:
        print("EXT_COUNTUR_MATCH_THRESHOLD --OK")

    ref_rect = cv2.minAreaRect(ref_ext_countour)
    test_rect = cv2.minAreaRect(test_ext_countour)

    (rcx, rcy), (rw, rh), rangle = ref_rect
    ref_center = (rcx, rcy)
    (tcx, tcy), (tw, th), tangle = test_rect
    test_center = (tcx, tcy)

    delta_angle = get_angle(ref_img, test_img)
    print(delta_angle)

    # draw_img(ref_bin_img, contour=ref_ext_countour, rect=ref_rect, center=ref_center,
    #        title="Ref image")

    # draw_img(test_img, contour=test_ext_countour, rect=test_rect, center=test_center, 
    #        title="Test image")

    print("Нажмите любую клавишу в окне изображения, чтобы закрыть его...")
    cv2.waitKey(0)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
