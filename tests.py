import cv2
import numpy as np

import img_process as ip

import constants as c
import roi as roi


def test1():
    ref_img = cv2.imread(c.ref_image_path)
    test_img = cv2.imread(c.test_image_path)
    
    ref_bin_img = ip.rgb2bin(ref_img)
    test_bin_img = ip.rgb2bin(test_img)
    
    ref_ext_countour = ip.external_countur_get(ref_bin_img)[0] # only first one
    test_ext_countour = ip.external_countur_get(test_bin_img)[0] # only first one
    
    match_value = cv2.matchShapes(ref_ext_countour, test_ext_countour, cv2.CONTOURS_MATCH_I1, 0.0)
    
    if match_value >= c.EXT_COUNTUR_MATCH_THRESHOLD:
        print("EXT_COUNTUR_MATCH_THRESHOLD --NG")
    else:
        print("EXT_COUNTUR_MATCH_THRESHOLD --OK")
    
    ref_rect = cv2.minAreaRect(ref_ext_countour)
    test_rect = cv2.minAreaRect(test_ext_countour)
    
    (rcx, rcy), (rw, rh), rangle = ref_rect
    (tcx, tcy), (tw, th), tangle = test_rect
    
    delta_angle = ip.get_angle(ref_img, test_img)
    print(delta_angle)

    cv2.namedWindow("Ref image", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Test image", cv2.WINDOW_NORMAL)
    
    img1 = ip.render_img(ref_bin_img, contour=ref_ext_countour, rectangle=True, center=True)
    cv2.imshow("Ref image", img1)

    img2 = ip.render_img(test_img, contour=test_ext_countour, rectangle=True, center=True)
    cv2.imshow("Test image", img2)
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

        contour = ip.external_countur_get(binary_img)
        if len(contour) > 0:
            contour = contour[0]
        else: contour = None

        img = ip.render_img(binary_img, contour=contour, contour_width=4, 
                   rectangle=True, rect_width=4, 
                   center=True, center_width=4)
        cv2.imshow("Test", img)
        
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

    state = roi.RefState()   

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can not get picture")
            break

        cur_center = None

        bin_frame = ip.rgb2bin(frame, low_threshold=160)
        contour = ip.external_countur_get(bin_frame)
        if len(contour) > 0:
            contour = contour[0]
            rect = cv2.minAreaRect(contour)
            cur_center = rect[0]

        state = roi.draw_roi(frame, state, cur_center)

        img = ip.render_img(frame, contour=contour, center=True)
        cv2.imshow("Test", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            state = roi.init_reference(frame)

    cap.release()
    cv2.destroyAllWindows()

def test4():
    import ocr
    ocr.get_reader()

    cv2.namedWindow("Test", cv2.WINDOW_NORMAL)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cam not found")
        return

    state = roi.RefState()
    last_text = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cur_center = None
        contour = None

        bin_frame = ip.rgb2bin(frame, low_threshold=160)
        contour = ip.external_countur_get(bin_frame)
        if len(contour) > 0:
            contour = contour[0]
            rect = cv2.minAreaRect(contour)
            cur_center = rect[0]

        state = roi.draw_roi(frame, state, cur_center)

        img = ip.render_img(frame, contour=contour, center=True)
        cv2.imshow("Test", img)

        if last_text:
            cv2.putText(frame, f"OCR: {last_text}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, c.GREEN, 2)
            cv2.imshow("Test", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            state = roi.init_reference(frame)
            last_text = None
        elif key == ord('o'):
            if state.ready and cur_center is not None:
                import ocr
                d_angle = state.prev_angle or 0.0
                roi_img = roi.extract_aligned_roi(frame, state, cur_center, d_angle)
                '''
                # debug
                if roi_img is not None:
                    cv2.imshow("ROI to OCR", roi_img)
                '''
                last_text = ocr.recognize(roi_img, allowlist=c.test_allowlist)
                print("--OCR:", last_text)
            else:
                print("--OCR: no ref or obj, press 'r'")

    cap.release()
    cv2.destroyAllWindows()


def main():
    test4()

if __name__ == "__main__":
    main()