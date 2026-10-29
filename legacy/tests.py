import cv2
import numpy as np
import legacy.ocr as ocr

import legacy.img_process as ip

import legacy.constants as c
import legacy.roi as roi
import legacy.process as process



def test1():
    ref_img = cv2.imread(c.ref_image_path)
    test_img = cv2.imread(c.test_image_path)
    
    ref_bin_img = ip.rgb2bin(ref_img)
    test_bin_img = ip.rgb2bin(test_img)
    
    ref_ext_countour = ip.get_main_contour(ref_bin_img)
    test_ext_countour = ip.get_main_contour(test_bin_img)
    
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
        print("--ERR: Cam not found")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("--ERR: Can not get picture")
            break

        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        global low_threshold_isChanged
        if low_threshold_isChanged:
            low_threshold = cv2.getTrackbarPos("Thresh low", "Test")
            low_threshold_isChanged = False

        _, binary_img = cv2.threshold(gray_img, low_threshold, 255, cv2.THRESH_BINARY)

        contour = ip.get_main_contour(binary_img)

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

    trackers = roi.RoiSet()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("--ERR: Can not get picture")
            break

        ctx = ip.build_context(frame)
        trackers.process(ctx)
        trackers.draw(frame)

        img = ip.render_img(frame, contour=ctx.main_contour, center=True)
        cv2.imshow("Test", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("--MES: Program finished")
            break
        elif key == ord('r'):
            tr = roi.init_reference(frame, name=f"roi_{len(trackers)}")
            if tr is not None:
                trackers.add(tr)
        elif key == ord('d') and len(trackers):
            trackers.remove(next(reversed(trackers.trackers)))

    cap.release()
    cv2.destroyAllWindows()

def test4():
    ocr.get_reader()

    cv2.namedWindow("Test", cv2.WINDOW_NORMAL)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("--ERR: Cam not found")
        return

    trackers = roi.RoiSet()
    last_texts: dict[str, str | None] = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        ctx = ip.build_context(frame)
        trackers.process(ctx)
        trackers.draw(frame)

        img = ip.render_img(frame, contour=ctx.main_contour, center=True)
        cv2.imshow("Test", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("--MES: Program finished")
            break
        elif key == ord('r'):
            cv2.destroyWindow("Test")
            tr = roi.init_reference(frame, name=f"roi_{len(trackers)}")
            if tr is not None:
                trackers.add(tr)
            last_texts = {}
            cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
            cv2.waitKey(1)
        elif key == ord('o'):
            if not trackers.ready():
                print("--OCR: no ref or obj, press 'r'")
                continue
            for name, roi_img in trackers.extract(frame).items():
                if roi_img is None:
                    continue
                txt = ocr.recognize(roi_img, allowlist=c.test_allowlist)
                last_texts[name] = txt
                print(f"--OCR [{name}]:", txt)

        if last_texts:
            overlay = frame.copy()
            for i, (name, txt) in enumerate(last_texts.items()):
                if txt:
                    cv2.putText(overlay, f"{name}: {txt}", (10, 30 + 30 * i),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, c.GREEN, 2)
            cv2.imshow("Test", overlay)

    cap.release()
    cv2.destroyAllWindows()

def test5():
    window_name = "Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("--ERR: Cam not found")
        return
    

    while True:
        ret, frame = cap.read()
        if not ret:
            print("--ERR: Can not get picture")
            break

        canvas = ip.render_img(frame)
        cv2.imshow(window_name, canvas)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("--MES: Program finished")
            break
        elif key == ord('r'):
            cv2.destroyWindow(window_name)
            Rois = process.ref_init(frame, c.precet_path)
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.waitKey(1)


    cap.release()
    cv2.destroyAllWindows()


def main():
    test5()

if __name__ == "__main__":
    main()