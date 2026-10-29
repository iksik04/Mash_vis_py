import json
import os
import cv2

from img_process import RefImgContext



def save_ref_context_to_json(ref_ctx: "RefImgContext",
                             output_dir: str = ".",
                             json_name: str = "Ref_img_context.json",
                             ref_img_name: str = "ref.jpg",
                             ref_bin_img_name: str = "ref_bin.jpg",
                             version: int = 1) -> str:
    """
    Save data from a RefImgContext instance to a JSON file.

    The JSON file contains:
      - version
      - reference_image       : filename of the saved BGR image
      - reference_bin_image   : filename of the saved binary image
      - reference_center      : [cx, cy] of the binarized image
      - reference_contour     : list of contour points [[x, y], ...]
      - params                : reference_low_threshold, min_ext_contour_length

    The BGR and binary images are written next to the JSON file.

    Returns the full path to the created JSON file.
    """
    if ref_ctx.ext_contour is None or ref_ctx.center is None:
        raise ValueError("--ERR: save_ref_context_to_json context is not built "
                         "(ext_contour/center is None). Call build_ref_context() first.")

    os.makedirs(output_dir, exist_ok=True)

    ref_img_path = os.path.join(output_dir, ref_img_name)
    ref_bin_img_path = os.path.join(output_dir, ref_bin_img_name)
    json_path = os.path.join(output_dir, json_name)

    # Save the original BGR image
    if not cv2.imwrite(ref_img_path, ref_ctx.bgr_img):
        raise IOError(f"--ERR: failed to write reference image to {ref_img_path}")

    # Save the binarized image (required for JSON consistency)
    if ref_ctx.bin_img is None:
        raise ValueError("--ERR: save_ref_context_to_json bin_img is None. "
                         "Call build_ref_context() first.")
    if not cv2.imwrite(ref_bin_img_path, ref_ctx.bin_img):
        raise IOError(f"--ERR: failed to write binary image to {ref_bin_img_path}")

    # Convert contour to a plain list of [x, y] float pairs
    contour_points = [[float(pt[0][0]), float(pt[0][1])] for pt in ref_ctx.ext_contour]

    data = {
        "version": version,
        "reference_image": ref_img_name,
        "reference_bin_image": ref_bin_img_name,
        "reference_center": [float(ref_ctx.center[0]), float(ref_ctx.center[1])],
        "reference_contour": contour_points,
        "params": {
            "reference_low_threshold": int(ref_ctx.ref_low_threshold),
            "min_ext_contour_length": int(ref_ctx.min_ext_contour_length),
        },
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return json_path