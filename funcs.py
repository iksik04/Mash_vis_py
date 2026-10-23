import cv2
import numpy as np

import constants as c


def roi_geometry(roi_offset, roi_w, roi_h, cur_center, angle_deg):
    """
    Единый источник истины для геометрии ROI.

    Соглашение:
      - angle_deg > 0 — поворот ПРОТИВ часовой стрелки в координатах кадра
        (ось X вправо, ось Y вниз — как принято в OpenCV).
      - Матрица поворота R = [[cos, -sin], [sin, cos]] (столбцовое соглашение:
        p' = R @ p).
      - roi_offset задан в СИСТЕМЕ КООРДИНАТ ОБЪЕКТА (повёрнутой вместе с ним).

    Возвращает:
      corners    — (4, 2) np.intp, углы ROI в координатах кадра (для отрисовки)
      roi_center — (2,) np.float32, центр ROI в координатах кадра
      R          — (2, 2) np.float32, матрица поворота объект -> кадр
    """
    a = np.radians(angle_deg)
    ca, sa = np.cos(a), np.sin(a)
    R = np.array([[ca, -sa],
                  [sa,  ca]], dtype=np.float32)

    ox, oy = roi_offset
    roi_center = (np.asarray(cur_center, dtype=np.float32)
                  + R @ np.array([ox, oy], dtype=np.float32))

    half = np.array([[-roi_w / 2.0, -roi_h / 2.0],
                     [ roi_w / 2.0, -roi_h / 2.0],
                     [ roi_w / 2.0,  roi_h / 2.0],
                     [-roi_w / 2.0,  roi_h / 2.0]], dtype=np.float32)

    corners = half @ R.T + roi_center          # (4, 2)
    return np.intp(corners), roi_center, R


# if __name__ == "__main__":
#    main()