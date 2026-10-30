import cv2

import constants as c
import img_process as ip
import json_process as js

def test1():

    ref_img = cv2.imread(c.ref_img_path)

    ref = ip.RefImgContext(bgr_img=ref_img, ref_low_threshold=40, min_ext_contour_length=50)
    ref.build_ref_context()

    js.save_ref_context(ref, output_dir=c.presets_path)
    # read_ref = js.read_ref_context(json_path="presets/ref_contexts/Ref_img_context.json")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test1()