import cv2
from dataclasses import dataclass, field

from .. import constants as c
from .. import img_process as ip
from .. import json_process as js
from ..ocr import getTextFromImg

@dataclass
class ValidationResult:
    ok: bool
    stage: str                    # "ext_contour" | "roi_contours" | "roi_symbols" | "ok"
    rois: dict = field(default_factory=dict)   # name -> bool|None
    symbols_info: dict = field(default_factory=dict)  # name -> {"expected": str, "recognized": str}
    message: str = ""

def checkExtContour(ref_contour, cur_contour):
    if ref_contour is None or cur_contour is None:
        return None
    match_value = cv2.matchShapes(ref_contour, cur_contour, cv2.CONTOURS_MATCH_I1, 0.0)
    return match_value <= c.EXT_COUNTUR_MATCH_THRESHOLD

def checkROIcontours(ref_rois, cur_rois, multi_roi):
    results = {}
    for name, roi in multi_roi.rois.items():
        ref_patch = ref_rois.get(name)
        cur_patch = cur_rois.get(name)

        if ref_patch is None or cur_patch is None:
            results[name] = None          # SKIP
            continue
        if roi.main_contour is None:
            results[name] = None          # SKIP
            continue

        thr = roi.cont_bin_threshold if roi.cont_bin_threshold is not None \
              else multi_roi.reference.ref_low_threshold
        min_len = roi.min_ext_cont_len if roi.min_ext_cont_len is not None \
                  else c.MIN_ROI_CONTOUR_LENGTH

        contours, _ = ip.extract_contours_from_bgr(cur_patch, thr, min_len)
        cur_contour = ip.pick_main_contour(contours,
                                           cur_patch.shape[1],
                                           cur_patch.shape[0])
        if cur_contour is None:
            results[name] = None          # SKIP
            continue

        match = cv2.matchShapes(roi.main_contour, cur_contour,
                                cv2.CONTOURS_MATCH_I1, 0.0)
        results[name] = match <= c.ROI_CONTOUR_MATCH_THRESHOLD
    return results

def checkROIsymbols(cur_rois, multi_roi, tess_allowlist=c.OCR_TEST_ALLOWLIST):
    if not isinstance(tess_allowlist, str) or tess_allowlist == "":
        raise ValueError("--ERR: checkROIsymbols tess_allowlist must be a non-empty str")

    results = {}
    info = {}
    for name, roi in multi_roi.rois.items():
        if not roi.OCR_allowlist:
            results[name] = None
            continue

        cur_patch = cur_rois.get(name)
        if cur_patch is None:
            results[name] = None
            continue

        thr = roi.ocr_bin_threshold if roi.ocr_bin_threshold is not None \
              else multi_roi.reference.ref_low_threshold

        text = getTextFromImg(cur_patch,
                              ocr_bin_threshold=thr,
                              allowlist=tess_allowlist)

        results[name] = (text != "" and text == roi.OCR_allowlist)
        info[name] = {"expected": roi.OCR_allowlist, "recognized": text}
    return results, info

def validate(frame, *, show: bool = True):
    multi_roi = js.read_MultiROI(c.MULTIROI_JSON_PATH, expected_version=2)

    cur = ip.CurImgContext(
        bgr_img=frame,
        ref_low_threshold=multi_roi.reference.ref_low_threshold,
        min_ext_contour_length=multi_roi.reference.min_ext_contour_length,
    )
    cur.reference = multi_roi.reference
    cur.build_cur_context()

    # --- Stage 1: external contour --------------------------------------
    ext_val = checkExtContour(cur.reference.ext_contour, cur.ext_contour)
    if ext_val is not True:                     # NG or SKIP
        result = ValidationResult(
            ok=False, stage="ext_contour",
            message="external contour mismatch" if ext_val is False
                    else "external contour unavailable",
        )
        if show: print_result(result)
        return result

    # --- Stage 2: ROI contours ------------------------------------------
    ref_rois = multi_roi.extract_all(frame=cur.reference.bgr_img,
                                     ref_center=cur.reference.center,
                                     delta_angle=0.0)
    cur_rois = multi_roi.extract_all(frame=cur.bgr_img,
                                     ref_center=cur.center,
                                     delta_angle=cur.delta_angle)
    roi_vals = checkROIcontours(ref_rois, cur_rois, multi_roi)

    # --- Stage 3: ROI symbols -------------------------------------------
    sym_vals, sym_info = checkROIsymbols(cur_rois, multi_roi)

    failed_cont = [n for n, v in roi_vals.items() if v is False]
    failed_sym  = [n for n, v in sym_vals.items() if v is False]
    ok = not failed_cont and not failed_sym

    if ok:
        stage = "ok"
    elif failed_cont and not failed_sym:
        stage = "roi_contours"
    elif failed_sym and not failed_cont:
        stage = "roi_symbols"
    else:
        # упали оба этапа — приоритет отдаём контурам (более ранний этап)
        stage = "roi_contours"

    if stage == "ok":
        message = ""
    elif stage == "roi_contours":
        message = f"failed ROIs (contours): {', '.join(failed_cont)}"
    else:  # roi_symbols
        message = f"failed ROIs (symbols): {', '.join(failed_sym)}"

    # объединённая карта name -> bool|None по обоим этапам
    rois_combined = {}
    for name in multi_roi.rois:
        vals = [d.get(name) for d in (roi_vals, sym_vals)]
        if any(v is False for v in vals):
            rois_combined[name] = False
        elif any(v is True for v in vals):
            rois_combined[name] = True
        else:
            rois_combined[name] = None

    result = ValidationResult(
        ok=ok, stage=stage,
        rois=rois_combined,
        symbols_info=sym_info,
        message=message,
    )
    if show: print_result(result)
    return result

def print_result(r: ValidationResult) -> None:
    print("=" * 60)
    if r.ok:
        print("--VAL OVERALL --OK")
        return

    print(f"--VAL OVERALL --NG  (stage: {r.stage})")
    if r.stage == "ext_contour":
        print(f"       {r.message}")
        print("=" * 60)
        return

    for name, v in r.rois.items():
        if v is False and name in r.symbols_info:
            exp = r.symbols_info[name]["expected"]
            rec = r.symbols_info[name]["recognized"]
            print(f"       ROI '{name}' --NG expected '{exp}', recognized '{rec}'")
        else:
            tag = "--OK" if v is True else "--NG" if v is False else "--SKIP"
            print(f"       ROI '{name}' {tag}")
    if r.message:
        print(f"       {r.message}")
    print("=" * 60)
