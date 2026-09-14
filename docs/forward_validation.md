# Forward HDSS preservation and native-reference agreement

The benchmark asks two different questions:

1. Can HDSS recover the original high-definition source body and retain its DVH
   under the same independent evaluator?
2. Does that independent evaluator reproduce the stored native TPS histogram?

The first check passes for the tested inputs. The second still has a material
residual and must not be described as solved.

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

The figure therefore retains the native residual. Agreement between the
original and recovered HDSS bodies must not be presented as native TPS
equivalence or proof that one TPS is clinically more accurate.

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
