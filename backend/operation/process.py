import cv2

"""
Grab a single frame from the camera at `cam_index` (default 0).

Requests 1920x1080 and releases the capture immediately.
Raises IOError if the frame cannot be read.
"""
def grab_frame(cam_index: int = 0):
    cap = cv2.VideoCapture(cam_index)
    frame = None
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        ok, frame = cap.read()
        cap.release()
        if ok and frame is not None:
            return frame
    if frame is None:
        raise IOError("--ERR: grab_frame can not get frame")
    return frame



#if __name__ == "__main__":
