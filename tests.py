import cv2
import numpy as np

import constants as c
import img_process as ip
import json_process as js
import roi as r
import roi_selector as roi_sel

def grab_frame(cam_index: int = 0):
    cap = cv2.VideoCapture(cam_index)
    frame = None
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        ok, frame = cap.read()
        cap.release()
        if ok and frame is not None:
            return frame
    if frame is None:
        raise IOError("--ERR: grab_frame can not get frame")
    return frame


def threshold_callback(x):
    return None
def setBinThereshold():
    windowName = "Set binaryzation thereshold"
    cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("Binary thereshold",  windowName, 160, 255, threshold_callback)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("--ERR: Can not open cam 0")
        exit()
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("--ERR: Can not get picture")
            break
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        low_threshold = cv2.getTrackbarPos("Binary thereshold", windowName)
        _, bin_img = cv2.threshold(gray_img, low_threshold, 255, cv2.THRESH_BINARY)
        cv2.imshow(windowName, bin_img)
    
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("--MES: Program finished")
            break
    
    cap.release()
    cv2.destroyAllWindows()


def test1():

    frame = grab_frame()

    reference = ip.RefImgContext(
        bgr_img=frame,
        ref_low_threshold=c.BINARYSATION_LOW_THRESHOLD,
        min_ext_contour_length=c.MIN_EXT_CONTOUR_LENGTH,
    )
    reference.build_ref_context()

    js.save_ref_context(reference, output_dir="presets/ref_contexts")

    multi_roi = r.MultiROI(reference=reference)
    window_name = "Select ROI"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    idx = 0
    try:
        while True:
            roi = roi_sel.select_single_roi(
                window_name=window_name,
                frame=frame,
                reference=reference,
                name=f"roi_{idx}",
                delta_angle_deg=0.0,
                initial=None,
                ocr_allowlist="",
            )
            if roi is None:
                break
            multi_roi.add(roi)
            idx += 1
    finally:
        cv2.destroyWindow(window_name)
        js.save_MultiROI(
            multi_roi,
            reference_context_path="presets/ref_contexts/Ref_img_context.json",
            output_dir="presets/ref_ROIs",
            json_name="MultiROI_context.json",
        )

    cv2.waitKey(0)

def change_low_threshold_callback(x):
    return None
def test2():
    frame = grab_frame()
    kernel = np.array([[ 0, -1,  0],
                   [-1,  5, -1],
                   [ 0, -1,  0]], np.float32)
    sharpened = cv2.filter2D(frame, -1, kernel)
    
    multi_roi = js.read_MultiROI("presets/ref_ROIs/MultiROI_context.json")

    cur = ip.CurImgContext(bgr_img=frame,
                           ref_low_threshold=c.BINARYSATION_LOW_THRESHOLD, 
                           min_ext_contour_length=c.MIN_EXT_CONTOUR_LENGTH)
    cur.reference = multi_roi.reference
    cur.build_cur_context()

    vis = multi_roi.render_all(frame=frame, 
                               ref_center=cur.center, 
                               delta_angle=cur.delta_angle)
    
    img_rois = multi_roi.extract_all(frame=frame, 
                                     ref_center=cur.center, 
                                     delta_angle=cur.delta_angle)

    cv2.namedWindow("ROI on current frame", cv2.WINDOW_AUTOSIZE)
    cv2.imshow("ROI on current frame", vis)

    for name, patch in img_rois.items():
        if patch is None:
            continue 
        win = f"ROI {name}"
        cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar("Thresh low",  f"ROI {name}", 160, 255, change_low_threshold_callback)
    
    while True:

        for name, patch in img_rois.items():
            win = f"ROI {name}"
            if patch is None:
                continue 
            resized = cv2.resize(patch, None, fx=5, fy=5)
            gray_img = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            low_threshold = cv2.getTrackbarPos("Thresh low", f"ROI {name}")
            _, bin_img = cv2.threshold(gray_img, low_threshold, 255, cv2.THRESH_BINARY)
            cv2.imshow(win, bin_img)
   
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("--MES: Program finished")
            break

    cv2.waitKey(0)
    cv2.destroyAllWindows()

def test3():
    windowName = "Test"
    cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("--ERR: Can not open cam 0")
        exit()

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("--ERR: Can not get picture")
            break
        cv2.imshow(windowName, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("--MES: Program finished")
            break

    cap.release()
    cv2.destroyAllWindows()
    
def test4():

    cv2.namedWindow("No filter", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Filtered", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Sharpened", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Sharpened2", cv2.WINDOW_AUTOSIZE)

    frame = grab_frame()    
    enhanced = cv2.detailEnhance(frame, sigma_s=10, sigma_r=0.15)

    kernel = np.array([[ 0, -1,  0],
                   [-1,  5, -1],
                   [ 0, -1,  0]], np.float32)
    sharpened = cv2.filter2D(frame, -1, kernel)

    kernel_sharpen = np.array([[-1, -1, -1],
                           [-1,  9, -1],
                           [-1, -1, -1]])
    sharpened2 = cv2.filter2D(frame, -1, kernel_sharpen)

    cv2.imshow("No filter", frame)
    cv2.imshow("Filtered", enhanced)
    cv2.imshow("Sharpened", sharpened)
    cv2.imshow("Sharpened2", sharpened2)

    cv2.waitKey(0)


if __name__ == "__main__":
    test2()