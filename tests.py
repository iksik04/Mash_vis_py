import cv2
import numpy as np

import constants as c
import funcs as f

def test1():
    ref_img = cv2.imread(c.ref_image_path)
    test_img = cv2.imread(c.test_image_path)
    
    ref_bin_img = f.rgb2bin(ref_img)
    test_bin_img = f.rgb2bin(test_img)
    
    ref_ext_countour = f.external_countur_get(ref_bin_img)[0] # only first one
    test_ext_countour = f.external_countur_get(test_bin_img)[0] # only first one
    
    match_value = cv2.matchShapes(ref_ext_countour, test_ext_countour, cv2.CONTOURS_MATCH_I1, 0.0)
    
    if match_value >= c.EXT_COUNTUR_MATCH_THRESHOLD:
        print("EXT_COUNTUR_MATCH_THRESHOLD --NG")
    else:
        print("EXT_COUNTUR_MATCH_THRESHOLD --OK")
    
    ref_rect = cv2.minAreaRect(ref_ext_countour)
    test_rect = cv2.minAreaRect(test_ext_countour)
    
    (rcx, rcy), (rw, rh), rangle = ref_rect
    ref_center = (rcx, rcy)
    (tcx, tcy), (tw, th), tangle = test_rect
    test_center = (tcx, tcy)
    
    delta_angle = f.get_angle(ref_img, test_img)
    print(delta_angle)
    
    f.draw_img(ref_bin_img, contour=ref_ext_countour, rect=ref_rect, center=ref_center,
            title="Ref image")
    
    f.draw_img(test_img, contour=test_ext_countour, rect=test_rect, center=test_center, 
            title="Test image")
    
    print("Нажмите любую клавишу в окне изображения, чтобы закрыть его...")
    cv2.waitKey(0)
    
    cv2.destroyAllWindows()

def main():
    test1()

if __name__ == "__main__":
    main()