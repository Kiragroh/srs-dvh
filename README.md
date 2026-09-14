# srs-dvh

[![Tests](https://github.com/Kiragroh/srs-dvh/actions/workflows/tests.yml/badge.svg)](https://github.com/Kiragroh/srs-dvh/actions/workflows/tests.yml)

**A 3D DVH builder for high-definition, HDSS-like structures**, with particular
attention to small SRS targets. Integrate the full supplied body in physical
coordinates, independently of CT slice spacing and dose-grid spacing.

**HDSS carries detailed structure information. It does not define how a DVH is
calculated.** A DVH also depends on the dose grid, the reconstructed boundary and
which volume is counted. Two programs can therefore read the same structure
information and still show different DVHs.

This builder evaluates the full supplied 3D body without reducing it to CT
slices. For a fair transfer comparison, keep the dose and calculation method
fixed and change only the structure representation.

**Accurate for which body?** Numerical accuracy is tested against known
mathematical dose fields and finer integration. This verifies the calculation
for its declared geometry; it does not establish that the geometry model
reproduces a native TPS's reconstructed boundary or sampled DVH volume.

![Surface/grid method: HDSS source preservation and separate native TPS agreement](docs/hdss_forward_validation.png)

**New in 0.2: choose full-volume integration or surface/grid evaluation.**
The figure now shows the surface/grid option. It reconstructs an explicit
surface and counts interior dose-grid points. All 120 source/HDSS pairs agree
exactly under this method; only 6/154 complete GTV histograms match the native
TPS. [Method, all-target results and runnable example](docs/surface_grid.md).

| Question | What is compared? | What does this benchmark show? |
|---|---|---|
| **A. Does HDSS retain the original target?** | Original target versus recovered HDSS target, using the same fine dose and the same 3D calculation. | Yes: all 120 target/plan representations recover the original source voxels. The checked dose metrics agree within 0.0001 Gy. |
| **B. Does our DVH match the native TPS?** | The stored native TPS DVH versus the selected independent method on the recovered HDSS target. | General agreement is not established. The evaluated volumes differ; the curve gap alone proves neither a TPS error nor damage caused by HDSS. |

**The common reference is a declared target, the same dose and the same verified
3D calculation.** HDSS can preserve the target information needed for that
comparison. It is not a universal DVH convention or automatically supported by
every receiving system. The 120 readouts comprise 72 planning targets plus 48
GTV evaluations in the PTV plans. [Evidence and scope](docs/forward_validation.md).

In one target, the complete source body occupies **5.952 mm³**, but the native
DVH counts **4.644 mm³**. A fixed surface-and-grid diagnostic reproduces that
histogram at unchanged fine dose. It reproduces only 2/24 complete histograms,
so it is evidence about evaluation choices, not a replacement reference or a
general native-TPS implementation.

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

The repository contains **18 tests** covering known spherical DVHs, oblique and
anisotropic coordinates, unequal volume weights, holes, tiny contour caps,
out-of-grid rejection and refinement checks.

The [analytical benchmark](examples/analytical_benchmark.py) uses four
sphere/ellipsoid configurations. At 0.025-mm integration spacing, its largest
absolute D98 error against the exact continuous-dose result is **0.0012 Gy**.
The largest curve error on the benchmark's stated plotting thresholds is
**0.157 percentage points**. These are results for those test fields, not a
universal accuracy guarantee. [Results and scope](docs/validation.md).

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
