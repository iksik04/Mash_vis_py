import os

# --- pathes ---------------------------------------------------------------
# constants.py lives in <root>/backend/, so the project root is one level up.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PRESETS_DIR       = os.path.join(_PROJECT_ROOT, "presets")
REF_CONTEXTS_DIR  = os.path.join(PRESETS_DIR, "ref_contexts")
REF_ROIS_DIR      = os.path.join(PRESETS_DIR, "ref_ROIs")
IMAGES_DIR        = os.path.join(_PROJECT_ROOT, "images")

# --- file names -----------------------------------------------------------
REF_CONTEXT_JSON_NAME = "Ref_img_context.json"
MULTIROI_JSON_NAME    = "MultiROI_context.json"
REF_IMG_NAME          = "ref.jpg"
REF_BIN_IMG_NAME      = "ref_bin.jpg"

# --- fully-resolved paths -------------------------------------------------
REF_CONTEXT_JSON_PATH = os.path.join(REF_CONTEXTS_DIR, REF_CONTEXT_JSON_NAME)
MULTIROI_JSON_PATH    = os.path.join(REF_ROIS_DIR,     MULTIROI_JSON_NAME)

# --- camera ---------------------------------------------------------------
CAM_INDEX = 0
CAM_WIDTH  = 1920
CAM_HEIGHT = 1080

# Colours
GREEN = (0, 255, 0)
BLUE  = (255, 0, 0)

# Line width
CONTOUR_LINE_WIDTH = 2
RECT_LINE_WIDTH    = 2
CENTER_LINE_WIDTH  = 2
ROI_LINE_WIDTH     = 1

MIN_EXT_CONTOUR_LENGTH = 50  # min contour len, pxl

# Thresholds
EXT_COUNTUR_MATCH_THRESHOLD = 0.011
ROI_CONTOUR_MATCH_THRESHOLD = 0.05

MIN_ROI_CONTOUR_LENGTH    = 50
ROI_CONTOUR_MIN_LEN_RANGE = 5000