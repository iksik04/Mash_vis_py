import cv2
from dataclasses import dataclass, field

from .. import constants as c
from .. import img_process as ip
from .. import json_process as js

@dataclass
class ValidationResult:
    ok: bool
    stage: str                    # "ext_contour" | "roi_contours" | "ok"
    rois: dict = field(default_factory=dict)   # name -> bool|None
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

    failed = [n for n, v in roi_vals.items() if v is False]
    ok = not failed

    result = ValidationResult(
        ok=ok, stage="roi_contours", rois=roi_vals,
        message="" if ok else f"failed ROIs: {', '.join(failed)}",
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
    elif r.stage == "roi_contours":
        for name, v in r.rois.items():
            tag = "--OK" if v is True else "--NG" if v is False else "--SKIP"
            print(f"       ROI '{name}' {tag}")
        if r.message:
            print(f"       {r.message}")
    print("=" * 60)
