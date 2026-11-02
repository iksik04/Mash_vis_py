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
        ok, frame = cap.read()
        cap.release()
        if ok and frame is not None:
            return frame
    if frame is None:
        raise IOError("--ERR: grab_frame can not get frame")
    return frame


def test1():

    frame = grab_frame()

    reference = ip.RefImgContext(
        bgr_img=frame,
        ref_low_threshold=c.BINARYSATION_LOW_THRESHOLD,
        min_ext_contour_length=c.MIN_EXT_CONTOUR_LENGTH,
    )
    reference.build_ref_context()

    js.save_ref_context(reference, output_dir="presets/ref_contexts")

    print("reference center:", reference.center)

    multi_roi = r.MultiROI(reference=reference)
    window_name = "Select ROI"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

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

    '''out_windows = []
    for name, roi in multi_roi.rois.items():
        patch = roi.extract(frame, ref_center=reference.center, delta_angle=0.0)
        if patch is None or patch.size == 0:
            print(f"--WARN: не удалось извлечь {name}")
            continue
        win = f"ROI: {name}"
        out_windows.append(win)
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)
        cv2.imshow(win, patch)'''
    cv2.waitKey(0)

def test2():
    frame = grab_frame()
    
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
    
    for name, patch in img_rois.items():
        if patch is None:
            continue 
        win = f"ROI {name}"
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)
        cv2.imshow(win, patch)



    cv2.namedWindow("ROI on current frame", cv2.WINDOW_NORMAL)
    cv2.imshow("ROI on current frame", vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()





if __name__ == "__main__":
    test2()