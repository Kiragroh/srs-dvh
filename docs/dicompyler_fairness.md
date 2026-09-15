# Ordinary DICOM deserves a fair comparator

`get_dvh` has options beyond its defaults. We checked version 0.5.6 using the
same ordinary contours and 1-mm exported dose for all 120 synthetic target/plan
states. None of the settings was selected by resemblance to a native TPS curve.

| Check | In-plane sampling | Inserted planes per interval | Explicit thickness |
|---|---:|---:|---:|
| Refined plane sampling | 0.125 mm | 0 | 1 mm |
| Finer sensitivity check | 0.0625 mm | 0 | 1 mm |
| Inserted-plane sensitivity | 0.125 mm | 7 | 1 mm |
| Finer inserted-plane sensitivity | 0.0625 mm | 15 | 1 mm |

The two in-plane settings changed D98 by at most 0.23 Gy; the 95th percentile
was 0.11 Gy. This is numerical sensitivity, not proof of physical accuracy.
Inserted planes copy the nearest existing contour in this version. They also
change endpoint weighting; a single-plane structure's volume is divided by the
subdivision count. This cannot recover missing fine source geometry.
[Implementation and options](https://dicompyler-core.readthedocs.io/en/latest/_modules/dicompylercore/dvhcalc.html).

## Check coordinates before interpreting refinement

A synthetic linear dose field, `D(x,y) = 10 + x + 2y Gy`, is exactly reproducible
by linear interpolation. In the optional 0.125-mm resampling tested here,
cropped dose pixels are image-rescaled while their reported coordinates span a
different endpoint convention. Interior sampled doses differed from the exact
field at those reported coordinates by a mean −1.50 Gy and maximum absolute
1.63 Gy. The requested 0.125-mm spacing was reported as 0.12727 mm in that crop.
These numbers belong to this deliberately chosen ramp, **not a clinical dose error**.

Direct interpolation at the actual physical coordinates reproduced the ramp
to below 1e-12 Gy. Run the [standalone audit](../examples/audit_dicompyler_resampling.py);
the [measured result](../examples/data/dicompyler_resampling_audit.json) is included.

The main figure holds the fine dose fixed in both panels and uses an independent coordinate-consistent
plane readout: sample dose on each supplied contour plane, weight by its exact
polygon area and declared 1-mm thickness, and sum the contributions. In-plane
sampling is 0.125 mm, checked at 0.0625 mm. It is a plane-based approximation,
not the proprietary algorithm of any TPS and not dicompyler-core with a hidden fix.
Default and optional-library curves remain in the synthetic example data.

The relevant comparison is **preserved fine information plus complete-volume
evaluation**. A library interpolation issue is not evidence for an HDSS benefit.
Nor does a remaining gap from the native TPS prove that either TPS is wrong.
