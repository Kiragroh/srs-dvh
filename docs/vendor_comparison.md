# Comparison protocol for vendors and researchers

Distinguish a change in the target representation from a change in the actual
dose field, and from a change in how a DVH is evaluated.

## 1. Establish numerical agreement on known inputs

Run the synthetic tests. Use identical geometry, physical coordinates and dose
samples in both evaluators. Record volume, D98, D95, D2, mean dose and cumulative
DVH differences. Specify interpolation, boundary inclusion and volume weighting.
Compare refinements; a smooth-looking plot is not a convergence test.

## 2. Test geometry transfer at fixed dose

Preserve the finest available reference geometry and input dose. Evaluate original
and transferred representations on **the same unchanged dose field**. Record both
the surface/mask volume and the volume actually included in the DVH. Separate
GTVs and PTVs; examine small volumes, elongation, obliquity and position relative
to image planes. Equal volume alone does not establish equal shape or DVH.

If source planes are finer than CT slices, preserve those planes or their explicitly
reconstructed 3D geometry throughout evaluation. Supporting HDSS import is
insufficient if evaluation discards its additional detail. The polygon-slab
adapter here is one explicit model; it is not a claim that every vendor uses it.

## 3. Test dose export separately

Hold the structure fixed. Compare original fine dose and exported dose on that
structure, using verified physical coordinates and the same integration method.
Fine quadrature cannot reconstruct information from a coarse exported dose grid.
Attribute this difference to dose representation, separately from geometry transfer.

## 4. Test replanning

Hold the planning template and intended optimisation settings fixed. Replan on
transferred targets. For each target, compare:

1. Original dose on original geometry.
2. New dose on original geometry.
3. New dose on transferred geometry.

The first two expose the dose-field change; the last two expose how the choice
of evaluated target changes the DVH. Report optimisation variability separately.

## Reproducibility record

Record software versions, source planes, geometry model, registrations, dose grid,
integration levels, volume weights, bin convention and convergence. Use the same
target mapping throughout. Do not fit shifts, scale factors or thresholds to force
agreement. Share synthetic or appropriately authorised data and an immutable code tag.
