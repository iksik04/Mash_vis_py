import cv2

import img_process as ip
import json_process as js

def test1():

    ref_img = cv2.imread("images/im1.jpg")

    ref = ip.RefImgContext(bgr_img=ref_img, ref_low_threshold=40, min_ext_contour_length=50)
    ref.build_ref_context()

    print(js.save_ref_context_to_json(ref))



    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test1()