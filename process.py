import cv2

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


def setBinThereshold():
    windowName = "Select binaryzation thereshold"
    cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("Binaryzation thereshold",  windowName, 160, 255, lambda x: None)

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
        low_threshold = cv2.getTrackbarPos("Binaryzation thereshold", windowName)
        _, bin_img = cv2.threshold(gray_img, low_threshold, 255, cv2.THRESH_BINARY)
        cv2.imshow(windowName, bin_img)
    
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("--MES: Program finished")
            break
    
    cap.release()
    cv2.destroyAllWindows()

def setRefContext():
    selectBinThereshWindowName = "Select binaryzation thereshold"
    cv2.namedWindow(selectBinThereshWindowName, cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("Binaryzation thereshold",  selectBinThereshWindowName, 127, 255, lambda x: None)
    bin_threshold_set = False
    select_ROI = False

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("--ERR: Can not open cam 0")
        exit()
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    print("--MES: Select binaryzation thereshold; press 'n' key if selected")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("--ERR: Can not get picture")
            break

        if not bin_threshold_set:
            bin_threshold = cv2.getTrackbarPos("Binaryzation thereshold", selectBinThereshWindowName)
            bin_img, ext_contour, _ = ip.extract_main_contour(frame, bin_threshold, c.MIN_EXT_CONTOUR_LENGTH)
            canvas = ip.render_img(image=bin_img, contour=ext_contour, center=True)
            cv2.imshow(selectBinThereshWindowName, canvas)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('n'):
            print(f"--MES: Selected {bin_threshold} binaryzation thereshold")
            bin_threshold_set = True
            select_ROI = True
            cv2.destroyWindow(selectBinThereshWindowName)
            break
        elif key == ord('q'):
            cv2.destroyAllWindows()
            print("--MES: Program finished")
            break

    if select_ROI:
            reference = ip.RefImgContext(
                bgr_img=frame,
                ref_low_threshold=bin_threshold,
                min_ext_contour_length=c.MIN_EXT_CONTOUR_LENGTH,
            )
            reference.build_ref_context()

            js.save_ref_context(reference, output_dir="presets/ref_contexts")

            multi_roi = r.MultiROI(reference=reference)
            selectROIWindowName = "Select ROI"
            cv2.namedWindow(selectROIWindowName, cv2.WINDOW_AUTOSIZE)

            idx = 0
            try:
                while True:
                    roi = roi_sel.select_single_roi(
                        window_name=selectROIWindowName,
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
                cv2.destroyWindow(selectROIWindowName)
                js.save_MultiROI(
                    multi_roi,
                    reference_context_path="presets/ref_contexts/Ref_img_context.json",
                    output_dir="presets/ref_ROIs",
                    json_name="MultiROI_context.json",
                )


if __name__ == "__main__":
    setRefContext()