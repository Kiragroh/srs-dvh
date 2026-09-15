# Source preservation and native agreement

The primary example uses one complete-volume evaluator at 0.05 mm and the same
fine dose for each original/returned pair. The source and recovered HDSS masks
are represented by unsmoothed level-0.5 surfaces. Ordinary contours use polygon
slabs. There is no target-specific shift, dose fitting or TPS-histogram tuning.

## Source preservation

For 120 target/plan readouts, source and recovered-HDSS D98 and evaluated volume
are identical. The maximum plotted curve difference is 0.000106 percentage
points. Original versus HDSS therefore overlaps in the
[paired figure](complete_3d_comparison.png). The separately checked source masks
retain their physical membership, orientation and spacing.

## Numerical sensitivity

All 120 references and their paired transfers/replans were calculated at 0.1
and 0.05 mm. Across paired D98 contrasts the 95th percentile change was 0.040 Gy
and the maximum 0.133 Gy. Nineteen cases selected for numerical sensitivity were
also checked at 0.025 mm: paired changes had p95 0.023 Gy
and maximum 0.125 Gy. This selected follow-up
does not prove universal convergence. Main figures retain one uniform 0.05-mm
setting; the residual sensitivity remains part of their interpretation.

Surface stencils are evaluated in local coordinates. Rounding those temporary
coordinates to 1e-8 mm and tolerating near-integer step counts prevents decimal
round-trip noise from adding an entire sample plane. Stored meshes are unchanged.
The boundary regression fails without this conditioning and passes with it.

## Native TPS comparison

The complete-volume result is **not uniformly closer to native TPS D98** than
the actual default ordinary-DICOM histogram readout. Paired mean absolute gaps
from the stored native scalar, in Gy:

| Plan / ROI | Complete 3D, fine dose | Default ordinary DICOM histogram |
|---|---:|---:|
| 0-mm / GTV | 0.578 | 0.408 |
| 1-mm / GTV | 0.247 | 0.178 |
| 1-mm / PTV | 0.315 | 0.311 |
| 2-mm / GTV | 0.087 | 0.126 |
| 2-mm / PTV | 0.291 | 0.226 |

These two workflows differ in geometry and dose representation, so the table
does not isolate integration alone. Native boundary-volume conventions remain
a separate source of difference. Neither comparator is used as a fitting target.

Default-library D98 lookup can return zero on a cumulative-volume plateau even
when its histogram is nonzero. The table uses the lower weighted quantile of
that original histogram, not that API lookup artifact. No missing DVH is filled
with zero. A default library result is not evidence of a commercial TPS algorithm.

## Reproduce the public figures

```sh
python examples/plot_complete_3d_comparison.py
python examples/plot_complete_3d_comparison.py --group 2 --output results/group2.png
```

The JSON contains all 120 synthetic target/plan readouts. Historical discrete
grid-centre and full-binary diagnostics remain in the repository for provenance;
they are not the current primary figure or a replacement for complete-volume
refinement. [Method contract](methods.md) · [Analytical tests](validation.md).
