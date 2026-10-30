import json
import os
import cv2
import numpy as np

from img_process import RefImgContext


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
def save_ref_context(ref_ctx: "RefImgContext",
                             output_dir: str = ".",
                             json_name: str = "Ref_img_context.json",
                             ref_img_name: str = "ref.jpg",
                             ref_bin_img_name: str = "ref_bin.jpg",
                             version: int = 1) -> str:
    
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
            "min_ext_contour_length": float(ref_ctx.min_ext_contour_length),
        },
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return json_path

"""
Read a reference image context from a JSON file.

The JSON file is expected to be in the format produced by
`save_ref_context_to_json` and to contain:
  - version             : format version (must match the expected one)
  - reference_image     : filename of the BGR image (relative to the JSON dir)
  - params              : reference_low_threshold, min_ext_contour_length

Builds a RefImgContext object, loads the BGR image

Returns the filled RefImgContext instance.
"""
def read_ref_context(json_path: str, expected_version: int = 1) -> "RefImgContext":
    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"--ERR: read_ref_context JSON not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # --- version check ---
    file_version = data.get("version")
    if file_version is None:
        raise ValueError("--ERR: read_ref_context JSON has no 'version' field")
    if int(file_version) != int(expected_version):
        raise ValueError(
            f"--ERR: read_ref_context version mismatch: "
            f"file={file_version}, expected={expected_version}"
        )

    # --- required fields check ---
    for key in ("reference_image", "reference_bin_image", "reference_center",
                "reference_contour", "params"):
        if key not in data:
            raise ValueError(f"--ERR: read_ref_context missing field: '{key}'")

    params = data["params"]
    for key in ("reference_low_threshold", "min_ext_contour_length"):
        if key not in params:
            raise ValueError(f"--ERR: read_ref_context missing params field: '{key}'")

    # --- load images relative to the JSON file ---
    base_dir = os.path.dirname(os.path.abspath(json_path))

    ref_img_path = os.path.join(base_dir, data["reference_image"])
    bgr_img = cv2.imread(ref_img_path, cv2.IMREAD_COLOR)
    if bgr_img is None:
        raise IOError(f"--ERR: read_ref_context failed to read image: {ref_img_path}")

    ref_bin_img_path = os.path.join(base_dir, data["reference_bin_image"])
    bin_img = cv2.imread(ref_bin_img_path, cv2.IMREAD_GRAYSCALE)
    if bin_img is None:
        raise IOError(f"--ERR: read_ref_context failed to read binary image: {ref_bin_img_path}")

    # --- restore contour ---
    contour_points = data["reference_contour"]
    ext_contour = np.array(contour_points, dtype=np.float32).reshape(-1, 1, 2)
    ext_contour = ext_contour.astype(np.int32)  # match OpenCV contour dtype

    # --- restore center ---
    center = (float(data["reference_center"][0]), float(data["reference_center"][1]))

    # --- build context ---
    ref_ctx = RefImgContext(
        bgr_img=bgr_img,
        ref_low_threshold=int(params["reference_low_threshold"]),
        min_ext_contour_length=float(params["min_ext_contour_length"]),
        bin_img=bin_img,
        ext_contour=ext_contour,
        center=center,
    )

    return ref_ctx