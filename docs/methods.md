# Method and input contract

For a less technical explanation, start with [How the DVH is calculated](dvh_explained.md).
The full-volume method below and the [discrete surface/grid method](surface_grid.md)
are separate evaluation options. The latter does not use subvoxel dose interpolation
or the full-volume convergence loop.

## Three independent resolutions

1. **Geometry:** the represented body, its boundary and physical position.
2. **Input dose:** a sampled dose field or a known continuous function.
3. **Integration:** how finely that body is integrated when evaluating the field.

Refining the third cannot restore information missing from either of the first
two. CT slice spacing is not imposed on the integration points.

## Physical coordinates and geometry

Coordinates are in millimetres. An affine maps the three array indices to voxel
centres in one common physical frame. Its columns define the array-axis directions
and spacings. Verify units, origin, slice order and any registration first.
No registration is estimated by this library.

`VoxelROI` subdivides each occupied voxel and retains its complete volume.
The determinant of its affine gives the voxel volume. A binary mask is not
silently converted to a smoothed mesh. Fractional masks are rejected because
they require an explicit interpretation.

`ImplicitROI` applies midpoint quadrature to a supplied mathematical predicate
inside its stated bounding box. Check refinement, particularly for boundaries.

`PolygonSlabROI` accepts polygons in local plane coordinates, an origin, an
orthonormal basis and one explicit depth interval per polygon. It clips the
in-plane integration cells to the polygon; clipped area times depth gives each
positive volume weight. Holes and tiny disconnected parts are retained. When a
clipped centroid lies outside the polygon, constrained triangulation supplies
interior quadrature points. Dose integration is approximate and must still be
refined even though these areas are exact within floating-point arithmetic.

This adapter describes prisms. It does not infer a continuous surface between
different polygons, end-cap conventions, gaps or a manufacturer's reconstruction.
Those choices must be established and documented by the calling reader.

`SurfaceROI` describes a supplied closed, consistently wound surface. With
`calculate`, it uses an interior midpoint grid and must be refined. With
`calculate_grid_centres`, it instead selects existing dose-grid centres strictly
inside the surface and gives them full dose-cell weights. These have different
boundary-volume definitions even when they use the same surface.

## Dose and the cumulative DVH

In full-volume integration, `DoseGrid` samples the supplied grid using trilinear interpolation. Evaluation
outside its centre-to-centre domain raises an error; there is no silent zero
padding or extrapolation. A callable can instead supply an analytical dose field.
Values are in Gy.

The discrete surface/grid function reads the stored grid values directly. Its
default requires the surface to fit in the dose-centre domain; the explicit
`available_grid` option examines only the supplied finite domain. It is not a
full-target coverage guarantee.

For doses `d_i` and positive physical volume weights `w_i`, the cumulative relative
DVH at threshold `t` is:

```text
V(t) = 100 × sum(w_i for d_i >= t) / sum(w_i)
```

`D_p` is the highest sampled dose received by at least `p` percent of the represented
volume. `D100` and `D0` return the sampled minimum and maximum. The weighted
empirical quantile does not interpolate across dose jumps. `Dmean` is the
volume-weighted mean. Plotting thresholds do not define integration or quantiles.
Neither spline smoothing nor curve fitting is used to manufacture TPS agreement.

## Convergence

`converge` evaluates a decreasing sequence of integration spacings. Two consecutive
refinements must each meet all three default criteria:

| Criterion | Default |
|---|---:|
| Maximum change among D98, D98.5, D95, D2 and Dmean | 0.02 Gy |
| Relative change in integrated volume | 0.2% |
| Maximum empirical DVH change over all observed dose thresholds | 0.25 percentage points |

The curve check evaluates the union of both distributions' observed dose thresholds
in bounded chunks. Narrow differences between plotting nodes cannot escape this
check. If the spacing sequence ends before two stable refinements, `converged`
is false. Additional integration levels can be supplied explicitly.

These checks show numerical stability for the selected model. They do not bound
every systematic input error, prove the exact geometry, validate a dose calculation
algorithm or establish equivalence with a TPS's internal DVH.

## Practical scope

The implementation stores dose samples and volume weights for sorting. It is
intended for small research targets, not unbounded whole-body sampling at extremely
fine spacing. It has no DICOM file reader, TPS connection or GPU backend. A reader
may be added around this core, provided it preserves the physical frame and states
the reconstruction model.
