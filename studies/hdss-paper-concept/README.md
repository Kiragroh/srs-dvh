# Small-target structure transfer: paper concept and reproducible figures

This concept-stage package supports a planned full Research Article in **Medical Physics**. It separates changes in target representation, fixed-dose DVH evaluation and replanning. It contains numerical results for synthetic targets, plotting code, editable tables and an anatomy-free analytical example. It is not a submitted manuscript or a clinical validation of a planning system.

## Run

```bash
python -m pip install numpy matplotlib
python build_figures.py
python synthetic_example.py
```

The first command pair regenerates five proposed main figures, an MR-to-CT supplement and two summary tables from the included extracts. The second example independently generates known spheres and a linear dose field, with exact spherical-cap D98 references. No TPS, network access or patient images are required for these reproductions. Recreating the original plans still requires the documented commercial systems and planning inputs; this package does not reproduce an optimizer.

## Contents and units

- `PAPER_PLAN.md`: questions, evidence, manuscript outline and remaining controls.
- `CAPTIONS.md`: complete draft English figure/table captions.
- `data/fixed_dose.csv`: 480 observed planning-target states; 432 complete six-route comparisons plus 48 observed Monaco states. Dose changes are transferred minus original, Gy; V20 changes are percentage points.
- `data/replanning.csv`: 96 PTV states from four coupled plans. All were optimised in the same source TPS.
- `data/native_curves.json.gz`: losslessly compressed native curves retained in original order, including duplicated-dose staircase points. Native export precision differs by system.
- `data/mr_ct.csv`: the same 24 GTV geometries on three original dose fields; 72 evaluations, not 72 independent geometries.
- `data/target_design.csv`: nominal and actual volumes, shape and sampling factors. Native binary and surface volumes are separate quantities.
- `data/target_positions.csv`: relative target centres in mm; no anatomy images.
- `figures/`: PNG previews and editable/vector PDF/SVG outputs.
- `tables/`: machine-readable and editable summary tables.

The main analysis uses 0.05-mm integration of declared geometries on fixed physical dose fields. This is numerical quadrature resolution, not the physical dose-grid resolution. Dice and volume columns use binary/contour-slab bodies; HDSS fixed-dose calculations recover source-grid surfaces. Zero HDSS differences are recovery consistency checks. No missing Monaco structure is silently replaced with a prediction.

## Provenance, rights and privacy

The anatomical source of the original benchmark is Yao S, Tan Y, Wang J. *A Paired Head CT-MRI Dataset for Cross-Modality Image Synthesis*. 2025. [doi:10.5281/zenodo.17486320](https://doi.org/10.5281/zenodo.17486320), meningioma/sub-01. On 26 September 2026 its live Zenodo API lists **CC BY-NC 4.0**, which supersedes the older CC BY 4.0 description in local preparation notes. Consult the source for current terms. CT/MR pixels are not redistributed here. Benchmark preparation used 1-mm slice spacing, a simulated oblique MR and clipping of 326 CT voxels above 3071 HU; this is a research preparation, not an untouched clinical planning CT.

All studied target contours are synthetic. No local clinical cohort, clinical screenshots, patient identifiers, DICOM instance UIDs, private correspondence or facial image pixels are included. Public source provenance remains cited. This reduces privacy exposure; it does not constitute an ethics-committee decision. The main paper must obtain and state the locally applicable determination for secondary use of public human-derived images. The new analytical example uses no human-derived data.

Code is covered by the repository's MIT license. Benchmark numeric extracts and their generated figures/tables are supplied under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), with the above source attribution; this is a conservative restriction for these derived research outputs and does not relicense the source images. The fully synthetic analytical generator is MIT-licensed code. UKL logos and clinical images are not part of this package.

## Reuse and contribution

Use the analytical example to check a DVH implementation, regenerate the paper figures, or contribute an additional observed transfer route. Preserve target identities, units, software versions, import options and the distinction between observed and model-generated structures. Report missing objects explicitly. New results should include reproducible inputs and numerical sensitivity checks; a visually smooth curve alone is not validation.

For double-anonymized peer review, use the separately prepared reviewer bundle without the public repository identity. Public posting can still make the work indirectly identifiable. A versioned archival DOI is planned after the analysis freeze; no new study DOI is claimed here.
