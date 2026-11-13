import cv2
import numpy as np

from backend import constants as c
from backend import img_process as ip
from backend import ocr
from backend import json_process as js
from backend.operation import process as p


"""
End-to-end test: read the MultiROI preset, detect the current frame's
reference context and rotation, render all ROIs, extract their patches,
then display a live, trackbar-controlled sharpened and binarized view of
each ROI. Press 'q' to exit.
"""
def test1():
    frame = p.grab_frame()
    
    multi_roi = js.read_MultiROI(c.MULTIROI_JSON_PATH, expected_version=2)

    cur = ip.CurImgContext(bgr_img=frame,
                           ref_low_threshold=multi_roi.reference.ref_low_threshold, 
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
        cv2.createTrackbar("k",  f"ROI {name}", 5, 10, lambda x: None)
        cv2.createTrackbar("bin",  f"ROI {name}", 80, 255, lambda x: None)
    
    while True:

        for name, patch in img_rois.items():
            win = f"ROI {name}"
            if patch is None:
                continue 
            k = cv2.getTrackbarPos("k", f"ROI {name}")
            bin_thereshold = cv2.getTrackbarPos("bin", f"ROI {name}")
            resized = cv2.resize(patch, None, fx=5, fy=5)
            sharpened = ip.img_sharpen(resized, k=k)
            gray_img = cv2.cvtColor(sharpened, cv2.COLOR_BGR2GRAY)
            _, bin_img = cv2.threshold(gray_img, bin_thereshold, 255, cv2.THRESH_BINARY)
            cv2.imshow(win, bin_img)
   
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("--MES: Program finished")
            break

    cv2.waitKey(0)
    cv2.destroyAllWindows()

"""
Continuously show frames from camera 0 at 1920x1080. Press 'q' to exit.
"""
def test2():
    windowName = "Test"
    cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)

    cap = cv2.VideoCapture(c.CAM_INDEX)
    if not cap.isOpened():
        print(f"--ERR: Can not open cam {c.CAM_INDEX}")
        exit()

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, c.CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, c.CAM_HEIGHT)

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

"""
Compare no filter, detail enhancement, and two sharpening kernels on a
single captured frame. Press any key to close.
"""
def test3():

    cv2.namedWindow("No filter", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Filtered", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Sharpened", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Sharpened2", cv2.WINDOW_AUTOSIZE)

    frame = p.grab_frame()    
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

def test4():

    frame = p.grab_frame()

    multi_roi = js.read_MultiROI(c.MULTIROI_JSON_PATH, expected_version=2)

    cur = ip.CurImgContext(
        bgr_img=frame,
        ref_low_threshold=multi_roi.reference.ref_low_threshold,
        min_ext_contour_length=multi_roi.reference.min_ext_contour_length,
    )
    cur.reference = multi_roi.reference
    cur.build_cur_context()

    cur_rois = multi_roi.extract_all(frame=cur.bgr_img,
                                     ref_center=cur.center,
                                     delta_angle=cur.delta_angle)
    name = "roi_0"
    roi_patch = cur_rois.get(name)

    text, prep_img = ocr.getTextFromImg(roi_patch, 75, debug=True)

    print(text)
    cv2.namedWindow(f"ROI {name}")
    cv2.imshow(f"ROI {name}", prep_img)

    cv2.waitKey(0)

if __name__ == "__main__":
    test4()