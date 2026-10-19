import cv2
import numpy as np

import constants as c
import funcs as f

def test1():
    ref_img = cv2.imread(c.ref_image_path)
    test_img = cv2.imread(c.test_image_path)
    
    ref_bin_img = f.rgb2bin(ref_img)
    test_bin_img = f.rgb2bin(test_img)
    
    ref_ext_countour = f.external_countur_get(ref_bin_img)[0] # only first one
    test_ext_countour = f.external_countur_get(test_bin_img)[0] # only first one
    
    match_value = cv2.matchShapes(ref_ext_countour, test_ext_countour, cv2.CONTOURS_MATCH_I1, 0.0)
    
    if match_value >= c.EXT_COUNTUR_MATCH_THRESHOLD:
        print("EXT_COUNTUR_MATCH_THRESHOLD --NG")
    else:
        print("EXT_COUNTUR_MATCH_THRESHOLD --OK")
    
    ref_rect = cv2.minAreaRect(ref_ext_countour)
    test_rect = cv2.minAreaRect(test_ext_countour)
    
    (rcx, rcy), (rw, rh), rangle = ref_rect
    (tcx, tcy), (tw, th), tangle = test_rect
    
    delta_angle = f.get_angle(ref_img, test_img)
    print(delta_angle)

    cv2.namedWindow("Ref image", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Test image", cv2.WINDOW_NORMAL)
    
    f.draw_img(ref_bin_img, contour=ref_ext_countour, rectangle=True, center=True,
            title="Ref image")
    
    f.draw_img(test_img, contour=test_ext_countour, rectangle=True, center=True, 
            title="Test image")
    
    print("Нажмите любую клавишу в окне изображения, чтобы закрыть его...")
    cv2.waitKey(0)
    
    cv2.destroyAllWindows()

low_threshold_isChanged = True

def change_low_threshold_callback(x):
    global low_threshold_isChanged
    low_threshold_isChanged = True

def test2():

    cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
    cv2.createTrackbar("Thresh low",  "Test", 160, 255, change_low_threshold_callback)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cam not found")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can not get picture")
            break

        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        global low_threshold_isChanged
        if low_threshold_isChanged:
            low_threshold = cv2.getTrackbarPos("Thresh low", "Test")
            low_threshold_isChanged = False

        _, binary_img = cv2.threshold(gray_img, low_threshold, 255, cv2.THRESH_BINARY)

        contour = f.external_countur_get(binary_img)
        if len(contour) > 0:
            contour = contour[0]
        else: contour = None

        f.draw_img(binary_img, contour=contour, contour_width=4, 
                   rectangle=True, rect_width=4, 
                   center=True, center_width=4,
                   title="Test")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def test3():
    cv2.namedWindow("Test", cv2.WINDOW_NORMAL)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cam not found")
        exit()

    have_ref = False

    ref_center = None          # (cx, cy) центра контура в момент выбора ROI
    ref_angle = 0.0            # угол контура в момент выбора ROI
    roi_offset = None          # (dx, dy) — смещение центра ROI относительно центра контура
    roi_w = roi_h = 0          # размеры ROI

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can not get picture")
            break

        # --- поиск текущего контура ---
        cur_center = None
        cur_angle = 0.0
        cur_cnt = None

        bin_frame = f.rgb2bin(frame)
        contours = f.external_countur_get(bin_frame)
        if len(contours) > 0:
            cur_cnt = contours[0]
            rect = cv2.minAreaRect(cur_cnt)
            cur_center = rect[0]
            cur_angle = rect[2]

        # --- отрисовка ROI, если эталон установлен и контур найден ---
        if have_ref and cur_center is not None:
            # смещение центра контура относительно эталона
            dcx = cur_center[0] - ref_center[0]
            dcy = cur_center[1] - ref_center[1]

            # поворот смещения ROI на дельту угла
            d_angle = cur_angle - ref_angle
            rad = np.radians(d_angle)
            cos_a, sin_a = np.cos(rad), np.sin(rad)
            ox, oy = roi_offset
            rot_ox = ox * cos_a - oy * sin_a
            rot_oy = ox * sin_a + oy * cos_a

            # новый центр ROI
            roi_cx = cur_center[0] + rot_ox
            roi_cy = cur_center[1] + rot_oy

            # поворот углов ROI на d_angle
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

            pts = np.intp(rotated)
            cv2.polylines(frame, [pts], True, c.BLUE, 2)

        f.draw_img(frame, title="Test")

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            roi_x0, roi_y0, roi_w, roi_h = cv2.selectROI(
                "Select ROI", frame, showCrosshair=True, fromCenter=False)
            cv2.destroyWindow("Select ROI")

            roi_cx = roi_x0 + roi_w / 2
            roi_cy = roi_y0 + roi_h / 2

            ref_bin_frame = f.rgb2bin(frame)
            ref_contours = f.external_countur_get(ref_bin_frame)
            if len(ref_contours) > 0 and roi_w > 0 and roi_h > 0:
                ref_rect = cv2.minAreaRect(ref_contours[0])
                ref_center = ref_rect[0]
                ref_angle = ref_rect[2]
                roi_offset = (roi_cx - ref_center[0], roi_cy - ref_center[1])
                have_ref = True
            else:
                have_ref = False

    cap.release()
    cv2.destroyAllWindows()


def main():
    test3()

if __name__ == "__main__":
    main()