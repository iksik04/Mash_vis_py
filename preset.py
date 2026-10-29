import json, os
import cv2

import img_process as ip
import roi

PRESET_VERSION = 1


def _rel(path, base):
    return os.path.relpath(path, base)


def save_preset(path_json, reference: ip.Reference, trackers: roi.RoiSet,
                params: dict | None = None) -> None:
    base = os.path.dirname(os.path.abspath(path_json))
    os.makedirs(base, exist_ok=True)

    img_name = os.path.splitext(os.path.basename(path_json))[0] + ".jpg"
    img_path = os.path.join(base, img_name)
    if not cv2.imwrite(img_path, reference.image):
        raise IOError(f"--ERR: cannot write reference image: {img_path}")

    data = {
        "version": PRESET_VERSION,
        "reference_image": _rel(img_path, base).replace("\\", "/"),
        "reference_center": [float(reference.center[0]), float(reference.center[1])],
        "rois": [
            {
                "name": t.name,
                "offset": [float(t.geometry.offset[0]), float(t.geometry.offset[1])],
                "w": float(t.geometry.w),
                "h": float(t.geometry.h),
                "angle": float(t.geometry.angle),
                "allowlist": t.allowlist,
            }
            for t in trackers.trackers.values()
        ],
        "params": params or {},
    }
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_preset(path_json) -> tuple[ip.Reference, roi.RoiSet, dict]:
    with open(path_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("version") != PRESET_VERSION:
        raise ValueError(f"unsupported preset version: {data.get('version')}")

    base = os.path.dirname(os.path.abspath(path_json))
    img_path = os.path.join(base, data["reference_image"])
    image = cv2.imread(img_path)
    if image is None:
        raise IOError(f"--ERR: cannot read reference image: {img_path}")

    center = tuple(map(float, data["reference_center"]))
    ref = ip.Reference(image=image, center=center)

    rs = roi.RoiSet(reference=ref)
    for r in data.get("rois", []):
        rs.add(roi.RoiTracker(
            name=r["name"],
            geometry=roi.RoiGeometry(
                offset=tuple(map(float, r["offset"])),
                w=float(r["w"]),
                h=float(r["h"]),
                angle=float(r.get("angle", 0.0)),
            ),
            allowlist=r.get("allowlist"),
        ))
    return ref, rs, data.get("params", {})