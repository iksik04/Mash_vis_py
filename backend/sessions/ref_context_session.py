import numpy as np

from .. import constants as c
from .. import img_process as ip


class RefContextSession:
    """
    Holds a frozen frame and rebuilds a RefImgContext whenever params change.

    Parameters
    ----------
    frame : np.ndarray
        BGR frame captured at the moment the session started (frozen).
    """

    def __init__(self, frame: np.ndarray):
        if frame is None or frame.size == 0:
            raise ValueError("--ERR: RefContextSession frame is empty")
        self._frame = frame.copy()
        self.bin_threshold: int = c.REF_CONTEXT_BIN_THRESHOLD
        self.min_contour_len: int = c.REF_CONTEXT_MIN_CONTOUR_LEN
        self._context: ip.RefImgContext | None = None
        self.rebuild()

    # ------------------------------------------------------------------
    @property
    def frame(self) -> np.ndarray:
        return self._frame

    @property
    def context(self) -> ip.RefImgContext:
        return self._context

    # ------------------------------------------------------------------
    def set_params(self, bin_threshold: int, min_contour_len: int) -> bool:
        """
        Update params and rebuild. Returns True if the params actually changed.
        """
        bt = int(bin_threshold)
        ml = int(min_contour_len)
        if bt == self.bin_threshold and ml == self.min_contour_len:
            return False
        self.bin_threshold = bt
        self.min_contour_len = ml
        self.rebuild()
        return True

    def rebuild(self) -> ip.RefImgContext:
        """Rebuild RefImgContext from the frozen frame and current params."""
        ctx = ip.RefImgContext(
            bgr_img=self._frame,
            ref_low_threshold=self.bin_threshold,
            min_ext_contour_length=self.min_contour_len,
        )
        ctx.build_ref_context()
        self._context = ctx
        return ctx

    # ------------------------------------------------------------------
    def preview_bin_img(self) -> np.ndarray:
        """Binarized frame for live preview."""
        return self._context.bin_img

    def preview_canvas(self) -> np.ndarray:
        """Binarized frame with the main contour rendered (BGR)."""
        return ip.render_img(
            image=self._context.bin_img,
            contours=[self._context.ext_contour],
            center=True,
        )