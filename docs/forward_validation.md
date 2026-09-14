# What HDSS preserves, and why a DVH can still differ

HDSS is a structure representation, not a DVH algorithm. The two figure panels
answer different questions; they are not alternative import routes.

The current figure defaults to the new [surface/grid option](surface_grid.md).
Use `--method full` to reproduce the earlier full-voxel-volume comparison.
The evidence below about full-volume integration remains separate from the
surface/grid results on all 154 individually stored GTV readouts.

- **A — preservation:** use the same fine dose and the same independent 3D
  calculation on the original target and the target recovered from HDSS.
  Agreement demonstrates source preservation under this evaluation.
- **B — native agreement:** compare a stored native TPS DVH with our independent
  calculation on the recovered HDSS target. Now the evaluation method changes.
  Agreement has not been established; this is not evidence of a vendor error.

For transfer studies, the common reference is explicitly defined geometry,
unchanged dose and one verified 3D method. Matching a proprietary native DVH is
a separate validation question. A system needs both preservation of the fine
structure and evaluation that uses that detail to benefit from HDSS.

## Forward input check

The source pixel planes were reconstructed from HDSS before comparison with the
original binary objects. Physical voxel locations, orientations, spacing and
membership were then checked. A fixed matrix-corner interpretation places the
in-plane pixel centres half a pixel from the declared corner. No native DVH,
target-specific shift or fitted threshold is used for this reconstruction.

All **120 GTV/PTV source bodies** matched, with zero changed source voxels.
Independently recomputed DVHs for **120 target/plan readouts** (72 planning
targets and 48 GTV readouts in the PTV plans), using the same local
fine dose and 0.05-mm full-volume integration, differed by at most:

| Quantity | Maximum absolute difference |
|---|---:|
| D98 | 0.000000001 Gy |
| D95 | 0.0000963 Gy |
| D2 | 0.000000001 Gy |
| Mean dose | 0.000000001 Gy |
| Curve at the specified plotting thresholds | 0.0000479 percentage points |

This validates the recovered **binary voxel body** for this benchmark. It does
not establish continuous-surface identity or universal importer conformance.
The core takes explicit physical-space geometry; the benchmark-specific DICOM
adapter is not part of the current package release.

## Native-reference check

The native histogram and the full binary body can use different evaluated
volumes. For one small target, the stored native DVH includes **4.644 mm³**,
whereas the full source body occupies **5.952 mm³**. The native boundary/inclusion
convention has not been reproduced for all targets. More quadrature points do
not, by themselves, resolve a difference in the represented volume.

The remaining gap has not been fully explained. Neither curve should be
labelled the clinical truth solely because it looks smoother or resembles a
TPS display. Independent accuracy on mathematical test cases and agreement
with a native TPS answer different questions.

The earlier comparison used the regular 1-mm dose export rather than the fine
local dose maps. It also used a different evaluated volume from the native TPS.
It therefore mixed dose representation and evaluation method; its separation
must not be attributed to structure export alone. Those earlier numerical
curves remain in the data as `regular_dose_pct`, but are not one of the two main
figure panels.

## Where can the native difference arise?

A fixed diagnostic on GTV01 keeps the fine dose field unchanged:

| Evaluated body / sampling | Counted volume [mm³] | D98 [Gy] |
|---|---:|---:|
| Complete source voxel body, fine integration | 5.952 | 18.72 |
| Fixed interpolated surface, fine integration | 5.730 | 19.32 |
| Only interior dose-grid centres of that surface | 4.644 | 20.78 |
| Stored native TPS DVH | 4.644 | 20.78 |

The fixed surface is an unsmoothed MC0.5 reconstruction, not an assertion about
the TPS's true internal surface. The first three rows use the same local dose
map. The grid-centre calculation reproduces the complete native histogram for
this target, but only **2/24 complete histograms** in the original GTV-only plan.
The extended source-frame/grid-matched comparison covers **154 GTV readouts
across seven plans**, with **6 exact histograms** in total, including those two.
These counts describe different scopes, not conflicting results. The method is
available for native comparisons; closer agreement alone is not a reason to
change the reference definition in a transfer study.

The remaining native-minus-grid-centre D98 differences range from −0.002 to
+0.958 Gy. Native reconstruction and sampling are therefore not fully
identified. The earlier 1-mm dose readout for GTV01 was 17.77 Gy: changing input
dose resolution alone changes that readout by 0.94 Gy under the same voxel-body
model. These sequential contrasts depend on the stated order; they are not
independent fractions of vendor error.

[All 24 numerical diagnostics](../examples/data/evaluation_components.json)
are included. Refining the surface integration from 0.05 to 0.025 mm changes
the checked metrics by at most 0.023 Gy and the full empirical DVH by 0.306
percentage points. That is a sensitivity check, not a proof of the native
boundary rule or a rigorous error bound.

## Reproduce the figure

```sh
python examples/plot_hdss_forward_validation.py
python examples/plot_hdss_forward_validation.py --group 2 --output results/targets_13_24.png
```

The whitelisted [numerical curves](../examples/data/hdss_forward_comparison.json)
contain all 24 synthetic GTVs. Each view selects 12 consecutive target numbers,
not the largest effects. The plotting script uses these measured curves; it
does not independently recalculate the benchmark's source dose. The separate
[analytical benchmark](../examples/analytical_benchmark.py) does calculate its
DVHs from mathematically defined inputs.

The figure/data contain no patient images, patient identifiers or native file
identifiers. All plotted comparisons are of evaluation methods, not a change
in delivered radiation.

## Coordinate definitions

The [DICOM ROI Contour Module, C.8.8.6](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.8.6.html)
describes the source-plane Image Position as the upper-left corner of the pixel
matrix. The ordinary [Image Plane Module, C.7.6.2](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.2.html)
defines the first transmitted voxel centre. This wording motivates the fixed
corner-to-centre conversion, which is empirically verified on these 120 source
bodies. It does not establish a universal half-pixel rule for every HDSS
exporter. The adapter's convention must be explicit and verified against source
geometry; it must not be fitted to make a DVH look better.
