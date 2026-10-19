import cv2
MIN_EXT_CONTOUR_LENGTH = 50  # минимальная длина периметра контура в пикселях

# Line width
CONTOUR_LINE_WIDTH = 8
RECT_LINE_WIDTH = 8
CENTER_LINE_WIDTH = 8

# Colours
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)

# Thresholds
EXT_COUNTUR_MATCH_THRESHOLD = 0.01
BINARYSATION_LOW_THRESHOLD = 160
BINARYSATION_HIGH_THRESHOLD = 255

# pathes
ref_image_path = "images/im1.jpg"
test_image_path = "images/im2.jpg"

key = cv2.waitKey(1) & 0xFF

# if __name__ == "__main__":
#    main()