import cv2
import img_process as ip
import roi
import preset


def ref_init(img, preset_path = None):
    ctx = ip.build_context(img)
    if ctx.center is None:
        print("--ERR: no main contour in captured frame")
        return None

    ref = ip.Reference(image=img.copy(), center=ctx.center)
    rs = roi.RoiSet(reference=ref)
    tr = roi.init_reference(img, ref.center, name=f"roi_{len(rs)}")
    if tr is not None:
        rs.add(tr)
    if preset_path is not None and len(rs):
        preset.save_preset(preset_path, ref, rs)
        print(f"--MES: preset saved to {preset_path}")
        return rs