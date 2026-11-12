import cv2
import numpy as np
import os

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

def setContourLenght():
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

    pending = {}   # name -> (thr, min_len, main_contour)  — подтверждённые в этой сессии
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

            # стартовые значения ползунков
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

                vis = ip._render_roi_contours(patch, contours, main_cnt, name, thr, min_len)
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

def validation():
    frame = grab_frame()
    
    multi_roi = js.read_MultiROI("presets/ref_ROIs/MultiROI_context.json")

    cur = ip.CurImgContext(bgr_img=frame,
                           ref_low_threshold=multi_roi.reference.ref_low_threshold, 
                           min_ext_contour_length=c.MIN_EXT_CONTOUR_LENGTH)
    cur.reference = multi_roi.reference
    cur.build_cur_context()

    vis = multi_roi.render_all(frame=frame, 
                              ref_center=cur.center, 
                              delta_angle=cur.delta_angle)

    ref_rois = multi_roi.extract_all(frame=cur.reference.bin_img, 
                                     ref_center=cur.reference.center, 
                                     delta_angle=0.0)
    
    cur_rois = multi_roi.extract_all(frame=cur.bin_img, 
                                     ref_center=cur.center, 
                                     delta_angle=cur.delta_angle)


    match_value = cv2.matchShapes(
        cur.reference.ext_contour, cur.ext_contour,
        cv2.CONTOURS_MATCH_I1, 0.0,
    )
    verdict = "--NG" if match_value >= c.EXT_COUNTUR_MATCH_THRESHOLD else "--OK"
    print(f"--VAL ext_contours {match_value:.3f} {verdict}")


    for name in multi_roi.rois:
        ref_patch = ref_rois.get(name)
        cur_patch = cur_rois.get(name)
        if ref_patch is None or cur_patch is None:
            print(f"--VAL ROI '{name}' --SKIP (patch is None)")
            continue

        cur_contour = ip.extract_contours(cur_patch, 100)
        
        if len(cur_contour) >= 2:
            cur_contour=cur_contour[1]   # sometimes outborder of image is contour, too
        elif len(cur_contour) == 1:
            cur_contour = cur_contour[0]
        elif len(cur_contour) < 1:
            print(f"--VAL ROI '{name}' --NG (no contours found)")
            break

        ref_contour = ip.extract_contours(ref_patch, 100)
        if len(ref_contour) >= 2:
            ref_contour=ref_contour[1]   # sometimes outborder of image is contour, too
        elif len(cur_contour) == 1:
            cur_contour = cur_contour[0]
        elif len(cur_contour) < 1:
            raise ValueError(f"--ERR: ROI '{name}' no contours found on ref image")

        
        # DEBAG
        cv2.namedWindow(f"Cur ROI {name}", cv2.WINDOW_AUTOSIZE)
        cur_canvas = ip.render_img(cur_patch, cur_contour)
        cv2.imshow(f"Cur ROI {name}", cv2.resize(cur_canvas, None, fx=4, fy=4))
     
        cv2.namedWindow(f"ref ROI {name}", cv2.WINDOW_AUTOSIZE)
        ref_canvas = ip.render_img(ref_patch, ref_contour)
        cv2.imshow(f"ref ROI {name}", cv2.resize(ref_canvas, None, fx=4, fy=4))

    
        roi_match = cv2.matchShapes(
            ref_contour, cur_contour,
            cv2.CONTOURS_MATCH_I1, 0.0,
        )
        roi_verdict = "--NG" if roi_match >= c.EXT_COUNTUR_MATCH_THRESHOLD else "--OK"
        print(f"--VAL ROI '{name}' matchShapes={roi_match:.3f} {roi_verdict}")

    cv2.namedWindow("validation", cv2.WINDOW_AUTOSIZE)
    cv2.imshow("validation", vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    validation()
    #setBinThereshold()