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

    ref_center = None       
    roi_offset = None         
    roi_w = roi_h = 0     

    ref_frame = None     
    prev_angle = None          

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can not get picture")
            break

        cur_center = None

        bin_frame = f.rgb2bin(frame, low_threshold=160)
        contour = f.external_countur_get(bin_frame)
        if len(contour) > 0:
            contour = contour[0]
            rect = cv2.minAreaRect(contour)
            cur_center = rect[0]

        if have_ref and cur_center is not None:
            d_angle = f.get_angle(ref_frame, frame)

            if prev_angle is not None:
                while d_angle - prev_angle > 180.0:
                    d_angle -= 360.0
                while d_angle - prev_angle < -180.0:
                    d_angle += 360.0
            prev_angle = d_angle

            pts = f.get_roi_corners(roi_offset, roi_w, roi_h, cur_center, d_angle)
            cv2.polylines(frame, [pts], True, c.BLUE, 2)

        f.draw_img(frame, title="Test", contour=contour, center=True)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            roi_x0, roi_y0, roi_w, roi_h = cv2.selectROI(
                "Select ROI", frame, showCrosshair=True, fromCenter=False)
            cv2.destroyWindow("Select ROI")

            roi_cx = roi_x0 + roi_w / 2
            roi_cy = roi_y0 + roi_h / 2

            ref_bin_frame = f.rgb2bin(frame, low_threshold=160)
            ref_contours = f.external_countur_get(ref_bin_frame)
            if len(ref_contours) > 0 and roi_w > 0 and roi_h > 0:
                ref_rect = cv2.minAreaRect(ref_contours[0])
                ref_center = ref_rect[0]
                roi_offset = (roi_cx - ref_center[0], roi_cy - ref_center[1])
                ref_frame = frame.copy()
                prev_angle = None
                have_ref = True
            else:
                have_ref = False

    cap.release()
    cv2.destroyAllWindows()


def main():
    test3()

if __name__ == "__main__":
    main()