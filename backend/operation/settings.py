import cv2
import numpy as np
import os
import pytesseract

from .. import constants as c
from .. import img_process as ip
from .. import json_process as js
from ..roi import roi as r
from ..roi import roi_selector as roi_sel
from ..ocr import getTextFromImg


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
def setRefContext(ref_context_output_dir: str = c.REF_CONTEXTS_DIR,
                  ref_context_json_name: str = c.REF_CONTEXT_JSON_NAME,
                  ref_ROI_output_dir: str = c.REF_ROIS_DIR,
                  ref_ROI_json_name: str = c.MULTIROI_JSON_NAME):
    selectBinThereshWindowName = "Select binaryzation thereshold"
    cv2.namedWindow(selectBinThereshWindowName, cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("Binaryzation thereshold",  selectBinThereshWindowName, 127, 255, lambda x: None)
    bin_threshold_set = False
    select_ROI = False

    cap = cv2.VideoCapture(c.CAM_INDEX)
    if not cap.isOpened():
        print(f"--ERR: Can not open cam {c.CAM_INDEX}")
        exit()
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, c.CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, c.CAM_HEIGHT)

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
    json_path: str = c.MULTIROI_JSON_PATH,
    output_dir: str = c.REF_ROIS_DIR,
    json_name: str = c.MULTIROI_JSON_NAME,
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
        reference_context_path=c.REF_CONTEXT_JSON_PATH,
        output_dir=output_dir,
        json_name=json_name,
        version=2,
    )
    print(f"--MES: setROIcontours saved {len(pending)} ROI(s) -> {os.path.join(output_dir, json_name)}")

# --- constants for the OCR-threshold tool ---------------------------------
_OCR_TEXT_MAX_LEN_ON_IMG = 20     # longer strings go to cmd as "Text in cmd"
_OCR_PREVIEW_MAX_WIDTH   = 1000   # preview is downscaled to <= this width
_OCR_FONT_SCALE          = 1.3    # ≈20 px glyph height for HERSHEY_SIMPLEX
_OCR_FONT_THICKNESS      = 2

_OCR_TB_PSM_MAX          = 13     # trackbar max for psm
_OCR_TB_MIN_SIDE_MIN     = 40     # trackbar min for ocr_min_side
_OCR_TB_MIN_SIDE_MAX     = 300    # trackbar max for ocr_min_side

"""
Render the OCR-preprocessed patch with the recognized text on top.

This function is DISPLAY-ONLY: it does not feed Tesseract. The patch is
resized (up or down, aspect ratio preserved) so that its width equals
`_OCR_PREVIEW_MAX_WIDTH` when possible, and its height stays <=
`c.CAM_HEIGHT` (protects very tall/narrow ROIs from overflowing the
screen). The recognized text is painted GREEN in the top-left corner
as "OCR: <text>" at ~20 px glyph height; when it is too long to fit
(by length or by rendered width), "OCR: Text in cmd" is painted.
"""
def _render_ocr_preview(prep_img, text):
    h, w = prep_img.shape[:2]
    s_w = _OCR_PREVIEW_MAX_WIDTH / float(w)
    s_h = float(c.CAM_HEIGHT)    / float(h)
    s   = min(s_w, s_h)          # up- or downscale, aspect preserved
    new_w = max(1, int(round(w * s)))
    new_h = max(1, int(round(h * s)))
    interp = cv2.INTER_AREA if s < 1.0 else cv2.INTER_CUBIC
    vis = cv2.resize(prep_img, (new_w, new_h), interpolation=interp)
    if vis.ndim == 2:
        vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

    label = text
    fits = (len(label) <= _OCR_TEXT_MAX_LEN_ON_IMG)
    if fits:
        (tw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX,
                                     _OCR_FONT_SCALE, _OCR_FONT_THICKNESS)
        fits = (tw + 10) <= vis.shape[1]
    if not fits:
        label = "Text in cmd"

    cv2.putText(vis, f"OCR: {label}", (5, 25),
                cv2.FONT_HERSHEY_SIMPLEX, _OCR_FONT_SCALE,
                c.GREEN, _OCR_FONT_THICKNESS, cv2.LINE_AA)
    return vis


"""
Interactively tune the OCR binarization threshold (and a few related
Tesseract / preprocessing parameters) for every ROI in a MultiROI file.

Workflow (per ROI):
  - `ocr_bin_threshold` (0..255), `psm` (0..13), `ocr_min_side` (40..300)
    are controlled by trackbars;
  - before the ROI is shown, `allowlist` is asked in the terminal
    (Enter = keep the current value);
  - live preview : binarized+upscaled patch with the recognized text
    painted GREEN in the top-left corner (or "Text in cmd" when it does
    not fit); the full text is always printed to cmd.

Controls:
  - 'n' / Enter / Space  - confirm current ROI
  - 's'                  - skip current ROI without changes
  - 'q'                  - save confirmed ROIs and exit
  - Esc                  - cancel the whole session (nothing saved)

Parameters
----------
json_path : str
    Path to the MultiROI JSON to edit.
output_dir : str
    Directory where the updated MultiROI JSON is written.
json_name : str
    File name of the updated MultiROI JSON.
"""
def setROI_OCRbinThereshold(
    json_path: str = c.MULTIROI_JSON_PATH,
    output_dir: str = c.REF_ROIS_DIR,
    json_name: str = c.MULTIROI_JSON_NAME,
):
    multi = js.read_MultiROI(json_path, expected_version=2)
    ref = multi.reference
    if ref.bgr_img is None:
        raise ValueError("--ERR: setROI_OCRbinThereshold reference.bgr_img is None")

    names = list(multi.rois.keys())
    if not names:
        print("--MES: setROI_OCRbinThereshold no ROIs to process")
        return

    win = "Set ROI OCR threshold"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("ocr_bin_threshold", win, 0,   255,                     lambda x: None)
    cv2.createTrackbar("psm",               win, 6,   _OCR_TB_PSM_MAX,         lambda x: None)
    cv2.createTrackbar("ocr_min_side",      win, 100,
                       _OCR_TB_MIN_SIDE_MAX, lambda x: None)

    pending = {}   # name -> (thr, psm, min_side, allowlist)
    idx = 0
    try:
        while idx < len(names):
            name = names[idx]
            roi  = multi.rois[name]

            patch = roi.extract(ref.bgr_img, ref.center, delta_angle=0.0)
            if patch is None or patch.size == 0:
                print(f"--WARN: setROI_OCRbinThereshold cannot extract '{name}', skip")
                idx += 1
                continue

            # ---- allowlist via terminal (B: per-ROI, Enter = keep) --------
            cur_allow = roi.OCR_allowlist or ""
            print(f"--MES: setROI_OCRbinThereshold [{idx+1}/{len(names)}] '{name}'")
            try:
                ans = input(f"       OCR_allowlist [current='{cur_allow}'] (Enter = keep): ")
            except EOFError:
                ans = ""
            allowlist = cur_allow if ans == "" else ans

            # ---- trackbar init -------------------------------------------
            thr0 = roi.ocr_bin_threshold if roi.ocr_bin_threshold is not None \
                   else ref.ref_low_threshold
            psm0 = 6
            min_side0 = 100
            cv2.setTrackbarPos("ocr_bin_threshold", win, int(thr0))
            cv2.setTrackbarPos("psm",               win, int(psm0))
            cv2.setTrackbarPos("ocr_min_side",      win,
                               int(min(max(min_side0, _OCR_TB_MIN_SIDE_MIN),
                                       _OCR_TB_MIN_SIDE_MAX)))
            cv2.setWindowTitle(win,
                f"Set ROI OCR threshold [{idx+1}/{len(names)}] {name}")

            while True:
                thr      = cv2.getTrackbarPos("ocr_bin_threshold", win)
                psm      = cv2.getTrackbarPos("psm",               win)
                min_side = cv2.getTrackbarPos("ocr_min_side",      win)
                if min_side < _OCR_TB_MIN_SIDE_MIN:
                    min_side = _OCR_TB_MIN_SIDE_MIN

                # OCR (raises TesseractNotFoundError — propagates on purpose)
                try:
                    text, prep_img = getTextFromImg(
                        patch,
                        ocr_bin_threshold=thr,
                        allowlist=allowlist,
                        psm=psm,
                        min_side=min_side,
                        debug=True,
                    )
                except pytesseract.TesseractNotFoundError:
                    raise
                except Exception as e:
                    text = f"<OCR error: {e}>"
                    prep_img = ip.OCR_imgPreprocess(patch, thr,
                                                    min_side=min_side)

                vis = _render_ocr_preview(prep_img, text)
                cv2.imshow(win, vis)

                key = cv2.waitKey(1) & 0xFF
                if key in (ord('n'), 10, 13, 32):
                    pending[name] = (int(thr), int(psm), int(min_side), allowlist)
                    idx += 1
                    break
                if key == ord('s'):
                    idx += 1
                    break
                if key == 27:                     # Esc
                    print("--MES: setROI_OCRbinThereshold cancelled, nothing saved")
                    return
                if key == ord('q'):
                    idx = len(names)
                    break
    finally:
        cv2.destroyWindow(win)

    # apply confirmed changes
    for name, (thr, psm, min_side, allowlist) in pending.items():
        roi = multi.rois[name]
        roi.ocr_bin_threshold = int(thr)
        roi.OCR_allowlist     = str(allowlist)
        # psm/min_side are runtime prefs, not stored in the JSON schema —
        # keep them only in-session (see note below).

    if not pending:
        print("--MES: setROI_OCRbinThereshold nothing confirmed, file not rewritten")
        return

    js.save_MultiROI(
        multi,
        reference_context_path=c.REF_CONTEXT_JSON_PATH,
        output_dir=output_dir,
        json_name=json_name,
        version=2,
    )
    print(f"--MES: setROI_OCRbinThereshold saved {len(pending)} ROI(s) "
          f"-> {os.path.join(output_dir, json_name)}")