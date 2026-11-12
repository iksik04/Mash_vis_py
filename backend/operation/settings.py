import cv2
import numpy as np
import os

from .. import constants as c
from .. import img_process as ip
from .. import json_process as js
from ..roi import roi as r
from ..roi import roi_selector as roi_sel


"""
Interactive tool to tune contour length and binarization thresholds.

Renders the extracted contours on a live camera feed, controlled by two
trackbars: "Contour lenght thereshold" and "Binaryzation thereshold".
Press 'q' to exit.
"""
def setContourLenghtBinThereshold():
    windowName = "Select contour lenght"
    cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("Contour lenght thereshold",  windowName, 500, 5000, lambda x: None)
    cv2.createTrackbar("Binaryzation thereshold",  windowName, 80, 255, lambda x: None)

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
        contour_lenght = cv2.getTrackbarPos("Contour lenght thereshold", windowName)
        low_threshold = cv2.getTrackbarPos("Binaryzation thereshold", windowName)
        _, bin_img = cv2.threshold(gray_img, low_threshold, 255, cv2.THRESH_BINARY)
        contours = ip.extract_contours(bin_img, contour_lenght)
        canvas = None
        canvas = ip.render_img(bin_img, contours)
        cv2.imshow(windowName, canvas)
    
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("--MES: Program finished")
            break
    
    cap.release()
    cv2.destroyAllWindows()

"""
Interactively build and save a reference context and its MultiROI set.

Workflow:
  1. Pick the binarization threshold on a live feed (press 'n' to confirm).
  2. Build a RefImgContext from the current frame and save it.
  3. Select zero or more rotated ROIs interactively and save them as a
     MultiROI JSON.

Parameters
----------
ref_context_output_dir : str
    Directory for the reference context JSON and its images.
ref_context_json_name : str
    File name of the reference context JSON.
ref_ROI_output_dir : str
    Directory for the MultiROI JSON.
ref_ROI_json_name : str
    File name of the MultiROI JSON.
"""
def setRefContext(ref_context_output_dir: str = "presets/ref_contexts",
                  ref_context_json_name: str = "Ref_img_context.json",
                  ref_ROI_output_dir: str = "presets/ref_ROIs",
                  ref_ROI_json_name: str = "MultiROI_context.json"):
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
            canvas = ip.render_img(image=bin_img, contours=[ext_contour], center=True)
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

            js.save_ref_context(reference, output_dir=ref_context_output_dir, json_name=ref_context_json_name)

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
                    reference_context_path=os.path.join(ref_context_output_dir, ref_context_json_name),
                    output_dir=ref_ROI_output_dir,
                    json_name=ref_ROI_json_name,
                )

"""
Interactively (re)define the main contour of each ROI and save the result.

For every ROI the reference patch is extracted and processed with a
trackbar-controlled binarization threshold and minimum contour length.
The picked main contour is stored in ROI-local coordinates.

Controls:
  - 'n' / Enter / Space — confirm current ROI
  - 's'                 — skip current ROI without changes
  - 'q'                 — save confirmed ROIs and exit
  - Esc                 — cancel the whole session (nothing saved)

Parameters
----------
json_path : str
    Path to the MultiROI JSON to edit.
output_dir : str
    Directory where the updated MultiROI JSON is written.
json_name : str
    File name of the updated MultiROI JSON.
"""
def setROIcontours(
    json_path: str = "presets/ref_ROIs/MultiROI_context.json",
    output_dir: str = "presets/ref_ROIs",
    json_name: str = "MultiROI_context.json",
):
    multi = js.read_MultiROI(json_path, expected_version=2)
    ref = multi.reference
    if ref.bgr_img is None:
        raise ValueError("--ERR: setROIcontours reference.bgr_img is None")

    names = list(multi.rois.keys())
    if not names:
        print("--MES: setROIcontours no ROIs to process")
        return

    win = "Set ROI contours"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.createTrackbar("cont_bin_threshold", win, 0, 255, lambda x: None)
    cv2.createTrackbar("min_ext_cont_len", win, 0, c.ROI_CONTOUR_MIN_LEN_RANGE, lambda x: None)

    pending = {}   # name -> (thr, min_len, main_contour)
    idx = 0
    try:
        while idx < len(names):
            name = names[idx]
            roi = multi.rois[name]

            patch = roi.extract(ref.bgr_img, ref.center, delta_angle=0.0)
            if patch is None or patch.size == 0:
                print(f"--WARN: setROIcontours cannot extract '{name}', skip")
                idx += 1
                continue

            thr0 = roi.cont_bin_threshold if roi.cont_bin_threshold is not None else ref.ref_low_threshold
            len0 = int(roi.min_ext_cont_len) if roi.min_ext_cont_len is not None else c.MIN_ROI_CONTOUR_LENGTH
            cv2.setTrackbarPos("cont_bin_threshold", win, int(thr0))
            cv2.setTrackbarPos("min_ext_cont_len", win, int(min(len0, c.ROI_CONTOUR_MIN_LEN_RANGE)))
            cv2.setWindowTitle(win, f"Set ROI contours [{idx+1}/{len(names)}] {name}")

            while True:
                thr = cv2.getTrackbarPos("cont_bin_threshold", win)
                min_len = float(cv2.getTrackbarPos("min_ext_cont_len", win))

                contours, bin_img = ip.extract_contours_from_bgr(patch, thr, min_len)
                main_cnt = ip.pick_main_contour(contours, patch.shape[1], patch.shape[0])

                vis = ip._render_roi_contours(bin_img, contours, main_cnt, name, thr, min_len)
                cv2.imshow(win, vis)

                key = cv2.waitKey(1) & 0xFF
                if key in (ord('n'), 10, 13, 32):
                    # фиксируем локальный контур (0..w, 0..h)
                    local_main = None
                    if main_cnt is not None:
                        local_main = main_cnt.reshape(-1, 1, 2).astype(np.int32)
                    pending[name] = (int(thr), float(min_len), local_main)
                    idx += 1
                    break
                if key == ord('s'):
                    idx += 1      # пропустить, не меняя
                    break
                if key == 27:     # Esc — отмена всей сессии
                    print("--MES: setROIcontours cancelled, nothing saved")
                    return
                if key == ord('q'):
                    # сохранить уже подтверждённое и выйти
                    idx = len(names)
                    break
    finally:
        cv2.destroyWindow(win)

    # применяем подтверждённые значения
    for name, (thr, min_len, main_cnt) in pending.items():
        roi = multi.rois[name]
        roi.cont_bin_threshold = thr
        roi.min_ext_cont_len = min_len
        roi.main_contour = main_cnt

    if not pending:
        print("--MES: setROIcontours nothing confirmed, file not rewritten")
        return

    js.save_MultiROI(
        multi,
        reference_context_path="presets/ref_contexts/Ref_img_context.json",
        output_dir=output_dir,
        json_name=json_name,
        version=2,
    )
    print(f"--MES: setROIcontours saved {len(pending)} ROI(s) -> {os.path.join(output_dir, json_name)}")