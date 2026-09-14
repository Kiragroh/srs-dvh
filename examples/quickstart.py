"""Standalone small-target example; no DICOM or patient data needed."""
import json
import numpy as np
from srs_dvh import ImplicitROI, converge


def main():
    radius = (3 * 6.5 / (4 * np.pi)) ** (1 / 3)
    center = np.array([0.13, -0.27, 0.49])

    def rho_squared(points):
        return np.sum((points - center) ** 2, axis=1) / radius**2

    roi = ImplicitROI(lambda p: rho_squared(p) <= 1, center-radius, center+radius)
    dvh, evidence = converge(roi, lambda p: 28 - 8*rho_squared(p),
                             steps=(0.1, 0.05, 0.025, 0.0125, 0.01))
    print(json.dumps({"metrics": dvh.metrics(), "evidence": evidence}, indent=2))
    if not evidence["converged"]:
        raise SystemExit("Integration did not meet the refinement criteria")


if __name__ == "__main__":
    main()
