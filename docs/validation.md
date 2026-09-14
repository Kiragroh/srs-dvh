# Validation evidence

## Analytical truth, independent of any TPS

Let `rho` be radius divided by surface radius in a sphere, or its corresponding
ellipsoidal coordinate. Inside the body, define:

```text
dose(rho) = 28 - 8 rho² Gy,   0 <= rho <= 1
V(d) = 100 ((28 - d) / 8)^(3/2)   for 20 <= d <= 28 Gy
D98 = 28 - 8 × 0.98^(2/3) Gy
Dmean = 23.2 Gy
```

The same exact distribution holds for affine ellipsoids because the volume
Jacobian is constant. No TPS curve is used as a fitted reference.

The benchmark contains two translated 6.5-mm³ spheres and oblique 30-/120-mm³
ellipsoids. Its committed [reference results](analytical_reference.json) use
0.025-mm integration for the final comparison. Across these four exact-field
cases, maximum absolute D98 error is approximately **0.001195 Gy** and maximum
curve error at the stated 281 thresholds is **0.156500 percentage points**.
Reproduce the figures and JSON with:

```sh
python examples/analytical_benchmark.py --output-dir results/analytical
```

The executable gates are D98 error <0.025 Gy, mean-dose error <0.02 Gy,
volume error <0.3%, and maximum curve error on those thresholds <0.35 percentage
points. This threshold-grid comparison against analytical truth is distinct from
the **exact empirical curve comparison** used by `converge`.

## What happens without adequate sampling?

The same script separately evaluates:

- only 1-mm planes, with exact continuous dose;
- complete 3D volume, with exact continuous dose;
- complete 3D volume, with sampled 1-, 0.4- and 0.1-mm dose fields.

One 6.5-mm³ case has approximately **3.65 Gy lower D98** after the deliberately
steep mathematical dose field is sampled on a 1-mm grid. That demonstrates a
possible input-dose sampling mechanism. It is **not a measured clinical error,
a typical effect size or a finding about a particular TPS**.

## Regression tests

The 25 collected tests include 18 core/contour tests covering sphere volumes, a spherical-cap DVH in a linear
field, oblique and anisotropic coordinates, occupied voxel volume, out-of-dose
rejection, refinement evidence, binary-mask validation, unequal weights, low-dose
curves, and a 50-percentage-point difference inside a 0.001-Gy interval invisible
on a coarser plotting grid.

Polygon tests include oblique tiny caps, holes, overlapping interval rejection,
interior sampling points for clipped cells and an oblique annulus in a known
quadratic field. The last case rejects coarse approximations and checks two
final metric refinements.

Seven surface tests additionally check a known cube, an oblique affine, the
single-voxel isosurface, open-surface rejection, empty grid support, explicitly
partial dose-grid coverage and a nested cavity in both signed-distance and
continuous-volume evaluation.

## Scope

The independent numerical model is reproducible. Equivalence to any proprietary
TPS's surface reconstruction, internal DVH volume or dose sampling is **not
established** by these tests. Numerical convergence, correct geometry interpretation
and agreement with a specific TPS are separate questions. A vendor comparison
must also test the reader, transformations and the original dose representation.
