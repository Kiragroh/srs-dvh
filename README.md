# srs-dvh

[![Tests](https://github.com/Kiragroh/srs-dvh/actions/workflows/tests.yml/badge.svg)](https://github.com/Kiragroh/srs-dvh/actions/workflows/tests.yml)

**A reusable 3D DVH builder for HDSS-derived and other high-definition structures.**

## The problem

A tiny SRS target may span only a few CT slices. Evaluating those sections alone
can give boundary regions the wrong weight in the DVH, even when the dose has
not changed. Finer structure information is useful only if the DVH calculation
also uses it.

## Our approach

**Preserve the 3D structure, then integrate dose throughout its volume.** Keep
the geometry and dose in the same physical coordinates. Divide the represented
body into small volume contributions, interpolate the available dose at each
contribution, and sum their volume weights. Refining the integration checks
whether the answer is stable. It does not require the integration points to lie
on CT slices.

![How coarse planes and fine volume integration represent a small target](docs/sampling_explained.svg)

Why this matters: a 6.5-mm³ sphere is only **2.32 mm across**. A few coarse
sections can give its boundary the wrong weight. Fine integration includes the
volume between those planes. The benefit is largest when targets are small or
thin and dose changes rapidly near the boundary. A properly reconstructed and
refined slice-based integrator can also be accurate; merely looping over slices
is not the problem.

## What the benchmark establishes

The figure keeps **the fine input dose and the complete 3D evaluator fixed**.
Left: original source geometry and geometry recovered from HDSS overlap.
Right: replacing that source with ordinary CT-plane contours changes the DVH.
The difference is due to the supplied geometry under this reconstruction model.

![Same dose and evaluator: HDSS retains the source readout; CT-plane contours can change it](docs/complete_3d_comparison.png)

Across 120 GTV/PTV source–HDSS pairs, D98 and integrated volume are identical;
the largest plotted curve difference is **0.00011 percentage points**. The
source/recovered masks use the same unsmoothed level-0.5 surface model. Ordinary
contours use explicit polygon slabs. Those body definitions are stated, not
silently treated as the same representation.

**This is a geometry-preservation result, not a claim to reproduce a TPS.**
The native TPS retains fine geometry and dose, but its boundary weights can
differ. Our complete-volume method is not uniformly closer to its stored D98
than an ordinary default DICOM readout. A favourable-looking DVH is not a
validation criterion. [Evidence and limits](docs/forward_validation.md).

The primary calculation is weighted complete-volume integration. The separate
[dose-grid-centre option](docs/surface_grid.md) remains available for diagnostics;
its whole-cell boundary weighting makes it sensitive to grid alignment.
Neither method can recover geometry or dose detail missing from the input.
[Illustrated explanation](docs/dvh_explained.md) · [Calculation details](docs/methods.md)

## Install and run

Python 3.10 or newer. Clone the repository and install locally:

```sh
git clone https://github.com/Kiragroh/srs-dvh.git
cd srs-dvh
python -m pip install -e ".[contours,surfaces,dev,examples]"
python examples/quickstart.py
python -m pytest tests -q
```

The package is distributed through this repository; these instructions do not
assume a PyPI release. NumPy and SciPy are the core dependencies. Shapely is
needed for the polygon adapter; scikit-image and VTK for the optional surface
adapter; Matplotlib for example figures.

## Use with your own arrays

```python
from srs_dvh import DoseGrid, VoxelROI, converge

# Arrays and affines must already describe the same physical coordinate frame.
dose = DoseGrid(dose_array_Gy, dose_index_to_world_affine)
roi = VoxelROI(binary_mask, roi_index_to_world_affine)
dvh, evidence = converge(roi, dose)

if not evidence["converged"]:
    raise RuntimeError("Integration has not met the refinement criteria")

print(dvh.metrics())
volume_percent = dvh.volume_at_dose([15, 18, 20, 22, 25, 28])
```

Coordinates are in **mm**, dose in **Gy**, volume weights in **mm³**. Each affine
maps array-index **voxel centres** to physical coordinates. There is no assumed
array-axis order: the affine columns define it. Verify registration first. No
shift, dose scaling or threshold is fitted to a reference TPS curve.

## Supported geometry

| Input | Evaluated volume |
|---|---|
| `VoxelROI` | Complete occupied binary voxels, including the outer half-voxel extent |
| `ImplicitROI` | A mathematical body specified by a physical-space predicate and bounding box |
| `PolygonSlabROI` | Polygons with holes and explicit slab intervals on parallel, possibly oblique planes |
| `SurfaceROI` with `calculate` | Interior of a supplied closed surface, using refined midpoint volume integration |
| Custom adapter | `quadrature(step_mm)` yielding physical points and positive volume weights |

High-definition source planes can be evaluated in their own basis without first
sampling them onto CT slices. The [oblique-contour example](examples/oblique_contours.py)
shows this interface. For DICOM RTSTRUCT or HDSS files, a separate reader must
supply the correct source planes, physical frame and geometric reconstruction.
This release is a numerical DVH builder, not a DICOM importer or HDSS file writer.

`PolygonSlabROI` integrates an **explicit polygon-prism model** using exact clipped
areas. It does not guess missing contours or a TPS-specific interpolation between
planes. See the [methods and input contract](docs/methods.md).

## Accuracy and examples

The repository contains **26 tests** covering known spherical DVHs, oblique and
anisotropic coordinates, unequal volume weights, holes, tiny contour caps,
out-of-grid rejection and refinement checks, plus surface reconstruction,
discrete grid sampling, nested cavities and explicit partial coverage.

The [analytical benchmark](examples/analytical_benchmark.py) uses four
sphere/ellipsoid configurations. At 0.025-mm integration spacing, its largest
absolute D98 error against the exact continuous-dose result is **0.0012 Gy**.
The largest curve error on the benchmark's stated plotting thresholds is
**0.157 percentage points**. These are results for those test fields, not a
universal accuracy guarantee. [Results and scope](docs/validation.md).

<details>
<summary>Methods appendix: mathematical accuracy and dose-grid effects</summary>

![Independent mathematical accuracy test](docs/analytical_srs_dvh.png)

*Separate analytic validation: a known 6.5-mm³ sphere in a deliberately steep
dose field. The exact reference is mathematical. These curves do not stand in
for the actual benchmark's native-TPS comparison.*

```sh
python examples/analytical_benchmark.py --output-dir results/analytical
```

This example separates **volume sampling** from **input dose-grid sampling**.
It exports a figure and machine-readable results showing what can otherwise be
lost. All inputs are mathematical objects; no patient data or TPS access is needed.

</details>

`converge` requires **two consecutive refinements** to satisfy dose-metric,
volume and curve tolerances. The curve comparison uses the exact maximum
difference between the two empirical DVHs over **all observed dose thresholds**,
independent of plotting bins. Always inspect the returned evidence.

Numerical convergence applies to the supplied dose and geometry. It does not
prove that those inputs reproduce a TPS's internal surface or DVH volume.
No TPS is launched and no input DICOM is changed.

## For vendors and researchers

High-definition geometry support and adequate DVH evaluation belong together:
discarding the additional geometry during evaluation can remove its benefit.
Input dose resolution also matters. The [comparison protocol](docs/vendor_comparison.md)
separates geometry transfer, dose representation, numerical integration and
replanning. Use analytical tests before comparing real plan data.

Research software; clinical use requires separate commissioning and validation.

## Cite and contribute

Use [CITATION.cff](CITATION.cff) and the specific release or commit for reproducible
references. No DOI or peer-reviewed validation paper is claimed by this release.
Reproducible issues and pull requests are welcome; use synthetic examples rather
than patient information. Licensed under [MIT](LICENSE).
