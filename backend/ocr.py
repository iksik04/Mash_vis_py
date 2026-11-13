import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\pkirill\AppData\Local\Tesseract-OCR\tesseract.exe"

from . import img_process as ip

# Tesseract configuration.
# --oem 3 : default LSTM engine.
# --psm 6 : "Assume a single uniform block of text" — good default for
#           ROI patches that contain one line / one block of text.
_OCR_LANG = "eng"
_OCR_OEM = 3
_OCR_PSM = 6


"""
Recognize text on a BGR image.

The image is preprocessed by `img_process.OCR_imgPreprocess` (hard
binarization with `ocr_bin_threshold`, auto-upscale of small images),
then passed to Tesseract.

Parameters
----------
img : np.ndarray
    BGR (or grayscale) image to recognize.
ocr_bin_threshold : int
    Threshold forwarded to `OCR_imgPreprocess`. Must be chosen so that
    the result is BLACK text on WHITE background (no inversion).
allowlist : str
    Characters Tesseract is allowed to output. Empty string = no
    restriction. Passed to Tesseract as `-c tessedit_char_whitelist=...`.
    Note: many builds ignore this with the LSTM engine (oem=3); the
    caller should still pass it since it works for some configs and
    is harmless otherwise.
lang : str
    Tesseract language, e.g. "eng", "rus". Default "eng".
psm : int
    Tesseract page segmentation mode. Default 6 (single uniform block).
debug : bool
    If True, also returns the preprocessed image used by Tesseract.

Returns
-------
text : str
    Recognized text (whitespace stripped).
prep_img : np.ndarray  (only when debug=True)
"""
def getTextFromImg(img, ocr_bin_threshold, allowlist="",
                   lang=_OCR_LANG, psm=_OCR_PSM, debug=False):
    prep_img = ip.OCR_imgPreprocess(img, ocr_bin_threshold, debug=False)

    config_parts = [f"--oem {_OCR_OEM}", f"--psm {int(psm)}"]
    if allowlist:
        config_parts.append(f"-c tessedit_char_whitelist={allowlist}")
    config = " ".join(config_parts)

    text = pytesseract.image_to_string(
        prep_img,
        lang=lang,
        config=config,
    )
    text = text.strip()

    if debug:
        return text, prep_img
    return text