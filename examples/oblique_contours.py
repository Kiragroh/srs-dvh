"""High-definition contour planes in their own oblique physical basis."""
import json
import numpy as np
from shapely.geometry import Point
from srs_dvh import calculate
from srs_dvh.contours import PolygonSlabROI


def main():
    # Three explicitly defined 0.2-mm slabs; no CT-grid resampling.
    contours = [Point(0, 0).buffer(r, quad_segs=64) for r in (0.8, 1.0, 0.8)]
    angle = np.deg2rad(30)
    basis = np.array([[1, 0, 0], [0, np.cos(angle), -np.sin(angle)],
                      [0, np.sin(angle), np.cos(angle)]])
    roi = PolygonSlabROI(contours, [[-0.3, -0.1], [-0.1, 0.1], [0.1, 0.3]],
                         np.array([0.13, -0.27, 0.49]), basis)
    dose = lambda p: 23 + p @ np.array([0.3, -0.2, 0.5])
    result = calculate(roi, dose, step_mm=0.025)
    assert abs(result.volume_mm3 - roi.volume_mm3) < 1e-9
    print(json.dumps(result.metrics(), indent=2))


if __name__ == "__main__":
    main()
