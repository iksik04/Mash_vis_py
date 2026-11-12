import cv2

from .. import constants as c
from .. import img_process as ip
from .. import json_process as js
from . import process as p

def validate():
    frame = p.grab_frame()

    multi_roi = js.read_MultiROI(c.MULTIROI_JSON_PATH,
                                 expected_version=2)

    cur = ip.CurImgContext(
        bgr_img=frame,
        ref_low_threshold=multi_roi.reference.ref_low_threshold,
        min_ext_contour_length=c.MIN_EXT_CONTOUR_LENGTH,
    )
    cur.reference = multi_roi.reference
    cur.build_cur_context()

    vis = multi_roi.render_all(frame=frame,
                               ref_center=cur.center,
                               delta_angle=cur.delta_angle)

    # Reference patches come from the stored BGR reference image so that
    # their coordinates match the `main_contour` saved by setROIcontours().
    ref_rois = multi_roi.extract_all(frame=cur.reference.bgr_img,
                                     ref_center=cur.reference.center,
                                     delta_angle=0.0)

    # Current patches come from the current BGR frame; the ROI-specific
    # threshold and min length are applied later, exactly as at save time.
    cur_rois = multi_roi.extract_all(frame=cur.bgr_img,
                                     ref_center=cur.center,
                                     delta_angle=cur.delta_angle)

    # --- external contour of the whole image ---
    match_value = cv2.matchShapes(
        cur.reference.ext_contour, cur.ext_contour,
        cv2.CONTOURS_MATCH_I1, 0.0,
    )
    ext_ng = match_value >= c.EXT_COUNTUR_MATCH_THRESHOLD
    print(f"--VAL ext_contours {match_value:.3f} {'--NG' if ext_ng else '--OK'}")

    any_ng = ext_ng

    # --- per-ROI validation ---
    for name, roi in multi_roi.rois.items():
        ref_patch = ref_rois.get(name)
        cur_patch = cur_rois.get(name)
        if ref_patch is None or cur_patch is None:
            print(f"--VAL ROI '{name}' --SKIP (patch is None)")
            continue

        # Reference contour is the one frozen by setROIcontours().
        if roi.main_contour is None:
            print(f"--VAL ROI '{name}' --SKIP (main_contour not set; run setROIcontours)")
            continue
        ref_contour = roi.main_contour

        # Current contour is obtained with the same chain as at save time
        # (binarize by ROI threshold -> find contours -> pick main).
        thr = roi.cont_bin_threshold if roi.cont_bin_threshold is not None \
              else multi_roi.reference.ref_low_threshold
        min_len = roi.min_ext_cont_len if roi.min_ext_cont_len is not None \
                  else c.MIN_ROI_CONTOUR_LENGTH

        contours, _ = ip.extract_contours_from_bgr(cur_patch, thr, min_len)
        cur_contour = ip.pick_main_contour(contours,
                                           cur_patch.shape[1],
                                           cur_patch.shape[0])
        if cur_contour is None:
            print(f"--VAL ROI '{name}' --NG (no main contour)")
            any_ng = True
            continue

        '''# Debug visualization (reference vs current).
        cur_canvas = ip.render_img(cur_patch, cur_contour)
        cv2.imshow(f"Cur ROI {name}", cv2.resize(cur_canvas, None, fx=4, fy=4))
        ref_canvas = ip.render_img(ref_patch, ref_contour)
        cv2.imshow(f"Ref ROI {name}", cv2.resize(ref_canvas, None, fx=4, fy=4))'''

        roi_match = cv2.matchShapes(ref_contour, cur_contour,
                                    cv2.CONTOURS_MATCH_I1, 0.0)
        roi_ng = roi_match >= c.ROI_CONTOUR_MATCH_THRESHOLD
        print(f"--VAL ROI '{name}' matchShapes={roi_match:.3f} "
              f"{'--NG' if roi_ng else '--OK'}")
        any_ng = any_ng or roi_ng

    print(f"--VAL OVERALL {'--NG' if any_ng else '--OK'}")

    #cv2.imshow("validation", vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
