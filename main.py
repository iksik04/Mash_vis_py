from backend.operation import validation
from backend.operation import settings
from backend.operation import visualize

from backend.operation import process
from backend import constants as c

from backend import json_process as js
import cv2

def main():
    frame = process.grab_frame()
    #validation.validate(frame)
    #settings.setContourLenghtBinThereshold()
    #settings.setRefContext()
    #settings.setROIcontours() 
    #settings.setROI_OCRbinThereshold() 
    multi_roi = js.read_MultiROI(c.MULTIROI_JSON_PATH, expected_version=2)
    result = validation.validate(frame, show=True)          # печать в stdout
    canvas = visualize.render_validation(frame, result, multi_roi)
    cv2.imshow("Validation", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()




if __name__ == "__main__":
    main()