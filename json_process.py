import json
import os
import cv2
import numpy as np

from img_process import RefImgContext
from roi import MultiROI, SingleROI


# ---------------------------------------------------------------------------
# Generic JSON helpers
# ---------------------------------------------------------------------------

"""
Write `data` as JSON to `path` with the project's standard formatting.

Creates parent directories if they do not exist. Raises IOError on failure.
"""
def _write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        raise IOError(f"--ERR: failed to write JSON to {path}: {e}") from e

"""
Read a JSON file and return the parsed dict.

Raises FileNotFoundError if the file does not exist, ValueError on parse errors.
"""
def _read_json(path: str) -> dict:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"--ERR: JSON not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"--ERR: invalid JSON in {path}: {e}") from e

"""
Validate the 'version' field of a parsed JSON dict against `expected`.

Raises ValueError if the field is missing or mismatched.
"""
def _check_version(data: dict, expected_version: int, caller: str) -> None:
    file_version = data.get("version")
    if file_version is None:
        raise ValueError(f"--ERR: {caller} JSON has no 'version' field")
    if int(file_version) not in (1, int(expected_version)):
        raise ValueError(
            f"--ERR: {caller} version mismatch: "
            f"file={file_version}, expected={expected_version}"
        )

"""
Ensure every key in `keys` is present in `data` (or in `data[section]`).

`section` is an optional nested dict name (e.g. "params"); when given, the
keys are checked inside `data[section]` and the prefix is included in the
error message for clarity.
"""
def _require_keys(data: dict, keys, caller: str, section: str | None = None) -> None:
    container = data
    prefix = ""
    if section is not None:
        if section not in data:
            raise ValueError(f"--ERR: {caller} missing field: '{section}'")
        container = data[section]
        prefix = f"{section}."

    for key in keys:
        if key not in container:
            raise ValueError(f"--ERR: {caller} missing field: '{prefix}{key}'")

"""
Parse a value that must be a 2-element sequence [a, b] of numbers.

Raises ValueError with a contextual message on failure.
"""
def _parse_pair(value, name: str, caller: str) -> tuple:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"--ERR: {caller} '{name}' must be [a, b]")
    try:
        return float(value[0]), float(value[1])
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"--ERR: {caller} '{name}' contains non-numeric values: {e}"
        ) from e

def _contour_to_list(cnt):
    if cnt is None:
        return None
    return [[float(pt[0][0]), float(pt[0][1])] for pt in cnt]

def _contour_from_list(data):
    if data is None:
        return None
    arr = np.array(data, dtype=np.float32).reshape(-1, 1, 2)
    return arr.astype(np.int32)

def _read_validation(r, caller):
    val = r.get("validation")
    if not isinstance(val, dict):
        # старый v1-файл или поле не задано — дефолты
        return {
            "ocr_allowlist": str(r.get("OCR_allowlist", "")),
            "main_contour": None,
            "ocr_bin_threshold": None,
            "cont_bin_threshold": None,
            "min_ext_cont_len": None,
        }
    data = val.get("data", {})
    params = val.get("params", {})
    return {
        "ocr_allowlist": str(data.get("ocr_allowlist", "")),
        "main_contour": _contour_from_list(data.get("main_contour")),
        "ocr_bin_threshold": params.get("ocr_bin_threshold"),
        "cont_bin_threshold": params.get("cont_bin_threshold"),
        "min_ext_cont_len": params.get("min_ext_cont_len"),
    }

# ---------------------------------------------------------------------------
# RefImgContext serialization
# ---------------------------------------------------------------------------
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
        raise ValueError("--ERR: save_ref_context context is not built "
                         "(ext_contour/center is None). Call build_ref_context() first.")
    if ref_ctx.bin_img is None:
        raise ValueError("--ERR: save_ref_context bin_img is None. "
                         "Call build_ref_context() first.")

    os.makedirs(output_dir, exist_ok=True)

    ref_img_path = os.path.join(output_dir, ref_img_name)
    ref_bin_img_path = os.path.join(output_dir, ref_bin_img_name)
    json_path = os.path.join(output_dir, json_name)

    if not cv2.imwrite(ref_img_path, ref_ctx.bgr_img):
        raise IOError(f"--ERR: failed to write reference image to {ref_img_path}")
    if not cv2.imwrite(ref_bin_img_path, ref_ctx.bin_img):
        raise IOError(f"--ERR: failed to write binary image to {ref_bin_img_path}")

    # Contour is stored as plain [x, y] float pairs.
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

    _write_json(json_path, data)
    return json_path

"""
Read a reference image context from a JSON file.

The JSON file is expected to be in the format produced by
`save_ref_context`. Builds a RefImgContext object and loads the BGR +
binary images from paths relative to the JSON file.

Returns the filled RefImgContext instance.
"""
def read_ref_context(json_path: str, expected_version: int = 1) -> "RefImgContext":
    data = _read_json(json_path)
    caller = "read_ref_context"

    _check_version(data, expected_version, caller)
    _require_keys(
        data,
        ("reference_image", "reference_bin_image",
         "reference_center", "reference_contour"),
        caller,
    )
    _require_keys(
        data,
        ("reference_low_threshold", "min_ext_contour_length"),
        caller,
        section="params",
    )

    params = data["params"]
    base_dir = os.path.dirname(os.path.abspath(json_path))

    ref_img_path = os.path.join(base_dir, data["reference_image"])
    bgr_img = cv2.imread(ref_img_path, cv2.IMREAD_COLOR)
    if bgr_img is None:
        raise IOError(f"--ERR: {caller} failed to read image: {ref_img_path}")

    ref_bin_img_path = os.path.join(base_dir, data["reference_bin_image"])
    bin_img = cv2.imread(ref_bin_img_path, cv2.IMREAD_GRAYSCALE)
    if bin_img is None:
        raise IOError(f"--ERR: {caller} failed to read binary image: {ref_bin_img_path}")

    ext_contour = np.array(data["reference_contour"], dtype=np.float32).reshape(-1, 1, 2)
    ext_contour = ext_contour.astype(np.int32)

    center = _parse_pair(data["reference_center"], "reference_center", caller)

    return RefImgContext(
        bgr_img=bgr_img,
        ref_low_threshold=int(params["reference_low_threshold"]),
        min_ext_contour_length=float(params["min_ext_contour_length"]),
        bin_img=bin_img,
        ext_contour=ext_contour,
        center=center,
    )


# ---------------------------------------------------------------------------
# MultiROI serialization
# ---------------------------------------------------------------------------
"""
Save a MultiROI instance to a JSON file.

The JSON file contains:
  - version
  - reference_context_file : path to the RefImgContext JSON file
                             (relative to the MultiROI JSON dir when possible)
  - rois                   : list of ROI dicts with
        name, offset, width, height, rotation_angle, OCR_allowlist

The reference context JSON file itself is NOT written here.

Returns the full path to the created JSON file.
"""
def save_MultiROI(multi_roi: "MultiROI",
                  reference_context_path: str,
                  output_dir: str = ".",
                  json_name: str = "MultiROI_context.json",
                  version: int = 1) -> str:

    if multi_roi is None:
        raise ValueError("--ERR: save_MultiROI multi_roi is None")
    if not isinstance(reference_context_path, str):
        raise ValueError("--ERR: save_MultiROI reference_context_path must be a str")
    if not os.path.isfile(reference_context_path):
        raise FileNotFoundError(
            f"--ERR: save_MultiROI reference context file not found: "
            f"{reference_context_path}"
        )

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, json_name)

    # Portable form of the reference context path.
    ref_ctx_abs = os.path.abspath(reference_context_path)
    base_dir = os.path.abspath(output_dir)
    try:
        ref_ctx_rel = os.path.relpath(ref_ctx_abs, base_dir)
    except ValueError:
        # Different drives on Windows — fall back to absolute.
        ref_ctx_rel = ref_ctx_abs

    rois_data = [
        {
            "name": roi.name,
            "offset": [float(roi.offset[0]), float(roi.offset[1])],
            "width": float(roi.width),
            "height": float(roi.height),
            "rotation_angle": float(roi.rotation_angle),
            "validation": {
                "data": {
                    "ocr_allowlist": str(roi.OCR_allowlist),
                    "main_contour": _contour_to_list(roi.main_contour),
                },
                "params": {
                    "ocr_bin_threshold": None if roi.ocr_bin_threshold is None else int(roi.ocr_bin_threshold),
                    "cont_bin_threshold": None if roi.cont_bin_threshold is None else int(roi.cont_bin_threshold),
                    "min_ext_cont_len": None if roi.min_ext_cont_len is None else float(roi.min_ext_cont_len),
                },
            },
        }
        for roi in multi_roi.rois.values()
    ]

    data = {
        "version": version,
        "reference_context_file": ref_ctx_rel,
        "rois": rois_data,
    }

    _write_json(json_path, data)
    return json_path

"""
Read a MultiROI instance from a JSON file.

The JSON file is expected to be in the format produced by `save_MultiROI`.
The reference context is loaded via `read_ref_context` and attached to the
returned MultiROI instance.

Returns the filled MultiROI instance.
"""
def read_MultiROI(json_path: str, expected_version: int = 1) -> "MultiROI":
    data = _read_json(json_path)
    caller = "read_MultiROI"

    _check_version(data, expected_version, caller)
    _require_keys(data, ("reference_context_file", "rois"), caller)

    # --- resolve the reference context path ---
    base_dir = os.path.dirname(os.path.abspath(json_path))
    ref_ctx_path = data["reference_context_file"]
    if not os.path.isabs(ref_ctx_path):
        ref_ctx_path = os.path.join(base_dir, ref_ctx_path)
    ref_ctx_path = os.path.normpath(ref_ctx_path)

    if not os.path.isfile(ref_ctx_path):
        raise FileNotFoundError(
            f"--ERR: {caller} reference context file not found: {ref_ctx_path}"
        )

    reference = read_ref_context(ref_ctx_path, expected_version=expected_version)

    rois_data = data["rois"]
    if not isinstance(rois_data, list):
        raise ValueError(f"--ERR: {caller} 'rois' must be a list")

    multi = MultiROI(reference=reference)

    roi_keys = ("name", "offset", "width", "height",
                "rotation_angle", "OCR_allowlist")
    for i, r in enumerate(rois_data):
        if not isinstance(r, dict):
            raise ValueError(f"--ERR: {caller} roi[{i}] must be an object")
        _require_keys(r, roi_keys, f"{caller} roi[{i}]")

        offset = _parse_pair(r["offset"], f"roi[{i}].offset", caller)

        v = _read_validation(r, caller)
        roi = SingleROI(
            name=str(r["name"]),
            offset=offset,
            width=float(r["width"]),
            height=float(r["height"]),
            rotation_angle=float(r["rotation_angle"]),
            OCR_allowlist=v["ocr_allowlist"],
            main_contour=v["main_contour"],
            ocr_bin_threshold=v["ocr_bin_threshold"],
            cont_bin_threshold=v["cont_bin_threshold"],
            min_ext_cont_len=v["min_ext_cont_len"],
        )
        multi.add(roi)  # raises KeyError on duplicate names

    return multi