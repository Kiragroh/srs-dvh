# How the DVH is calculated, and why small targets need care

A DVH answers: **what fraction of the evaluated target receives at least a given
dose?** The answer depends on the target boundary, the available dose information
and how physical volume is counted. HDSS can preserve fine structure information;
the evaluator must still use it.

![Coarse plane sampling, fine volume sampling, and the relative importance of a 1-mm slab](sampling_explained.svg)

## The direct HDSS comparison

The [main figure](hdss_sampling_comparison.png) holds the recovered HDSS surface
and fine input dose map fixed. It compares actual 1-mm CT-plane-only sampling
with the 3D surface/grid method. Across the 24 original GTVs, mean absolute D98
disagreement with the native TPS falls from **0.601 to 0.234 Gy**; mean-dose
disagreement falls from **0.309 to 0.096 Gy**. This is improved agreement with
the native comparator, whose remaining differences stay visible.

The coarse method uses 0.025-mm midpoint sampling within each CT plane, a 1-mm
depth weight and trilinear dose interpolation. Its 0.05-to-0.025-mm in-plane
refinement changes D98 by at most 0.062 Gy. The 3D method instead reads existing
fine dose-grid centres inside the same surface. Thus this comparison changes
both depth sampling and the dose-sampling rule. It does not test every possible
slice-based implementation. The displayed curves share 0.2-Gy bins; each is
normalized to its own evaluated volume. Scalar dose metrics are unbinned.

The [numerical evidence](../examples/data/hdss_sampling_comparison.json) includes
all 24 targets. Rebuild either twelve-target panel group from the repository root:

```sh
python examples/plot_hdss_sampling_comparison.py
python examples/plot_hdss_sampling_comparison.py --group 2 --output results/group2.png
```

## What “slice by slice” means here

The limited comparison in this project evaluates selected cross-sections, assigns
each the represented slice thickness, and sums their dose histograms. If those
planes are 1 mm apart, making only the in-plane pixels smaller still does not
measure how the target boundary and dose vary between the planes. A tiny target
can be represented by only a few sections. Moving it relative to the planes can
then substantially change the sampled volume and dose distribution.

**Processing slices in a loop is not itself a problem.** A method that correctly
reconstructs the body, integrates between planes, handles boundaries and converges
with refinement can also be accurate. The advantage described here is over a
coarse plane-only readout, not over every algorithm described as “slice by slice”.
For example, dicompyler-core exposes separate in-plane and between-plane
interpolation options. Our deliberately limited comparison does not establish
the performance of every setting. [Documented API and implementation](https://dicompyler-core.readthedocs.io/en/latest/_modules/dicompylercore/dvhcalc.html).

## Method 1 — integrate physical volume

This is the method used for the common, fixed-dose transfer comparisons.

1. **Keep the supplied geometry in physical coordinates.** Source voxels retain
   their orientation and complete extent. Contour inputs retain their declared
   source planes and explicit depth intervals; they are not forced onto CT slices.
   A supplied surface is another explicit body model.
2. **Split the body into small contributions throughout its depth.** With a
   0.4-mm binary source voxel and a requested 0.05-mm step, each voxel contributes
   8 × 8 × 8 subvoxels. For polygon slabs, boundary cells are clipped and their
   actual area is multiplied by the integration depth; holes remain excluded.
   Surface integration uses interior midpoint cells and is refined separately.
3. **Evaluate dose at each point.** For a sampled dose grid, trilinear
   interpolation uses the surrounding eight dose values. The supplied dose
   arrays remain unchanged. A known continuous dose can instead be passed directly.
4. **Add physical volume, not just point counts.** At 20 Gy, for example, sum the
   volume weights of all contributions receiving at least 20 Gy, then divide by
   the total evaluated volume. D98 is derived from the weighted dose distribution;
   mean dose uses the same weights.
5. **Refine and check stability.** `converge` requires two consecutive refinements
   to meet its volume, dose-metric and full-curve tolerances. The 0.05-mm step used
   in benchmark comparisons is an integration setting, not a new dose resolution.

```text
V(20 Gy) [%] = 100 × volume receiving at least 20 Gy / evaluated target volume
Dmean       = sum(dose × represented volume) / sum(represented volume)
```

**Why this helps:** the calculation includes volume between the source planes
and resolves dose variation within the represented body. It reduces sensitivity
to a coarse evaluation lattice. It cannot recover geometry already discarded
during export, invent missing dose detail, or determine an undocumented TPS
boundary. A finely integrated polygon-prism model remains a polygon-prism model.

## Method 2 — count dose-grid centres inside a surface

This selectable method investigates native TPS readouts. It is also spatially
three-dimensional, but it is a **discrete sampled-volume method**:

1. Reconstruct a closed, unsmoothed surface from binary voxels at level 0.5,
   or supply a closed surface explicitly.
2. Keep the existing dose-grid centres strictly inside that surface.
3. Use the dose value stored at each retained centre, without dose interpolation.
   Assign each point one complete dose-cell volume. Boundary cells are not
   fractionally weighted.
4. Calculate the weighted cumulative histogram and dose metrics from those points.

For example, 172 retained points on a 0.3-mm isotropic dose grid represent
172 × 0.3³ = **4.644 mm³**. In one benchmark target, that matches the native DVH
volume, while the complete source voxels occupy **5.952 mm³**. This changes which
boundary dose contributes, even though the input dose map is unchanged.

The surface/grid option comes closer to the native DVH in this benchmark. That
does **not** make it a generally more accurate full-volume integral. Its result
can depend strongly on dose-grid spacing and alignment, especially for tiny
targets. In 130/298 diagnostic readouts, the chosen local grid has a smaller
centre extent than the surface; the explicitly requested `available_grid` mode
counts only its available points. [Exact input contract and results](surface_grid.md).

## Why the relative effect is larger for small structures

A 6.5-mm³ sphere is about **2.32 mm in diameter**. A central 1-mm-thick slab
contains approximately **61%** of its volume. The same slab contains only
**7.5%** of a 20-mm-diameter sphere. These are geometric fractions, **not predicted
DVH errors**: one coarse section has much more relative influence on the small
object. For spheres, surface area divided by volume is 3/r; the relative amount
near a boundary therefore grows as the radius decreases.

When dose falls steeply at that boundary, omitted or overweighted portions can
strongly affect low-tail coverage metrics such as D98. Elongation, obliquity and
position between planes also matter. In larger targets with gentle gradients,
fine and coarse evaluations may differ little, and extreme refinement can add
cost with little benefit. Large size alone is not a guarantee: thin extensions
or a steep boundary gradient can still need fine evaluation.

## What is established, and what remains a separate question

| Question | Evidence |
|---|---|
| Does fine full-volume integration work for its stated inputs? | Analytical and refinement tests verify the numerical calculation for specified geometry and dose. |
| Can HDSS retain the information needed by either method? | All 120 benchmark source bodies are recovered exactly; paired DVHs agree within 0.0001 Gy for checked full-volume metrics and exactly for the surface/grid method. |
| Have we reproduced the native TPS algorithm? | The 3D HDSS method is closer overall than the tested coarse-plane readout, while residual differences remain. This is a reusable approach rather than a claim to reproduce an undocumented native algorithm exactly. |

The DICOM source-plane description permits planes independent of actual image
slices and supports retaining the originating grid. It does not select a DVH
integration method. [DICOM PS3.3, C.8.8.6.4](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.8.6.4.html).

For a fair transfer comparison, hold the dose and evaluation rule fixed, preserve
the finest available source geometry, and report the evaluated volume. For native
TPS agreement, explicitly test its boundary and sampling conventions as a separate
question. A smoother curve or a more favourable D98 is not an accuracy test.

[API details and convergence tolerances](methods.md) · [Analytical examples](validation.md)
