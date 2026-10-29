import cv2

import img_process as ip

def test1():

    ref_img = cv2.imread("images/im1.jpg")

    ref = ip.RefImgContext(bgr_img=ref_img, ref_low_threshold=40, min_ext_contour_length=50)

    cv2.namedWindow("Ref image", cv2.WINDOW_NORMAL)

    cv2.imshow("Ref image", ref.bin_img)

if __name__ == "__main__":
    test1()