import cv2

import constants as c
import img_process as ip
import json_process as js
from roi import MultiROI
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
        raise IOError("Не удалось получить кадр ни с камеры, ни из файла")
    return frame


def test1():

    frame = grab_frame()

    reference = ip.RefImgContext(
        bgr_img=frame,
        ref_low_threshold=c.BINARYSATION_LOW_THRESHOLD,
        min_ext_contour_length=c.MIN_EXT_CONTOUR_LENGTH,
    )
    reference.build_ref_context()
    print("reference center:", reference.center)

    multi = MultiROI(reference=reference)
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
            multi.add(roi)
            idx += 1
            print(f"Added {roi.name}: offset={roi.offset}, "
                  f"w={roi.width:.1f}, h={roi.height:.1f}, "
                  f"angle={roi.rotation_angle:.2f}")

            ans = input("Добавить ещё ROI? [Y=да / N=нет]: ").strip().lower()
            if ans == "n":
                break
    finally:
        cv2.destroyWindow(window_name)

    out_windows = []
    for name, roi in multi.rois.items():
        patch = roi.extract(frame, ref_center=reference.center, delta_angle=0.0)
        if patch is None or patch.size == 0:
            print(f"--WARN: не удалось извлечь {name}")
            continue
        win = f"ROI: {name}"
        out_windows.append(win)
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)
        cv2.imshow(win, patch) 
    cv2.waitKey(0)


if __name__ == "__main__":
    test1()