# Surface and dose-grid-centre DVHs

> Diagnostic option. The current primary workflow is complete-volume integration; see [source preservation and numerical checks](forward_validation.md). Closer agreement with a stored TPS curve does not establish full-volume accuracy.

[Start with the illustrated explanation of both methods](dvh_explained.md).

Version 0.2 adds a selectable surface/grid method alongside full-volume
integration. It is useful when investigating a TPS that evaluates a reconstructed
surface at discrete dose points. It is **not a verified copy of a native TPS
algorithm** and does not automatically replace full-volume integration.

“Closer to the native TPS” describes the measured benchmark agreement. It does
not establish greater numerical accuracy for the complete target volume or an
automatic advantage over a sufficiently refined slice-based integrator.

```bash
python -m pip install -e ".[surfaces]"
```

```python
from srs_dvh import VoxelROI, SurfaceROI, DoseGrid, calculate, calculate_grid_centres

# Both affines map array indices to physical voxel centres, in millimetres.
source = VoxelROI(binary_mask, source_affine)
dose = DoseGrid(dose_values_Gy, dose_affine)
surface = SurfaceROI.from_voxels(source)

full_voxel_dvh = calculate(source, dose, step_mm=0.05)
full_surface_dvh = calculate(surface, dose, step_mm=0.05)
surface_grid_dvh = calculate_grid_centres(surface, dose)
```

The three results answer different geometric/sampling questions:

| Method | Body | What contributes to the DVH? |
|---|---|---|
| Full voxel volume | Complete union of occupied source voxels | Positive subvoxel volume weights |
| Full surface volume | Unsmoothed marching-cubes surface at binary level 0.5 | Interior midpoint volume weights |
| Surface/grid | The same reconstructed surface | Only interior dose-grid centres, each assigned a full dose-cell volume |

Boundary cells in the last method are not fractionally weighted. Its reported
volume is the sampled volume and may differ from `surface.mesh_volume_mm3`.
The fixed strict-interior rule uses a numerical boundary tolerance of 1e-6 mm.
Mesh triangles must be closed and consistently wound, with cavity shells facing
into cavities. The adapter preserves this relative winding. Self-intersections
are outside the supported input contract.

The default requires the grid to enclose the whole surface. A separate explicit
option, `coverage="available_grid"`, counts only available grid centres even if
the surface extends beyond their domain. It does not extrapolate dose or certify
full-target coverage. This option exists to examine tightly cropped stored
evaluation grids; it is not an automatic fallback.

## What the benchmark establishes

- All **154 individually stored GTV readouts** across seven plans were checked,
  plus **144 PTV readouts**. These reuse 24 synthetic target geometries; they are
  not 154 independent lesions or patients.
- The method improves native agreement in the measured coarse-plane comparison.
  Remaining native boundary/readout differences stay visible.
- All **120 original-versus-recovered-HDSS pairs** produce exactly the same
  surface/grid curves and checked dose metrics. The method can therefore be
  applied to these recovered HDSS source bodies without losing the source result.

For this native-comparison diagnostic, the local input map is chosen using its
recorded source frame and native DVH spacing, then geometric extent and size.
A one-cell extent allowance accommodates tight grids. No native DVH values are
used to choose the map, contour threshold or surface. Those file-format-specific
map rules are part of the benchmark adapter, not hidden inside the public API.
In **130/298** readouts, surface vertices extend beyond the dose-centre extent;
these deliberately use the finite available domain, not a full-target integral.

For the plotted native comparison, both curves use the same 0.2-Gy histogram
bins, each normalized by its own evaluated volume. This removes a display-only
binning difference without fitting the curves or changing the dose samples.
The reported scalar dose metrics are calculated from unbinned samples.

| Original plan | GTV readouts | Mean absolute D98 difference from native [Gy] | Largest absolute D98 difference [Gy] |
|---|---:|---:|---:|
| GTV-only | 24 | 0.234 | 0.958 |
| 1-mm margin | 24 | 0.083 | 0.273 |
| 2-mm margin | 24 | 0.028 | 0.074 |

Replan GTV comparisons have mean absolute D98 differences of 0.074–0.239 Gy,
with a largest individual difference of 1.597 Gy. Better numerical agreement is
not by itself evidence that a geometric definition is more accurate.

[All 154 GTV numerical comparisons](../examples/data/surface_grid_comparison.json)
and the [earlier fixed-dose/body diagnostic](forward_validation.md) are included.

```bash
python examples/surface_grid.py
python examples/plot_hdss_forward_validation.py --method surface
python examples/plot_hdss_forward_validation.py --method full --output results/full_volume.png
```
