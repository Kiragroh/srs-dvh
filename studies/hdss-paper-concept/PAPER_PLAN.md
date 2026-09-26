# Paper concept — 26 September 2026

**Working title:** Structure-transfer and dose-volume evaluation effects in small-target radiosurgery: an open high-definition benchmark

**Target:** Medical Physics, full Research Article. **Alternative:** Journal of Applied Clinical Medical Physics if the editors prefer a practice-focused framing. **Authors:** to be agreed; no authorship order is inferred. **Status:** concept and existing-result figures, not a finished or submitted manuscript.

## Central contribution

A reproducible benchmark distinguishes geometry-dependent changes on a fixed dose field, discrepancies between native and common DVH readouts, and the consequences of replanning on transferred targets. Agreement of two native DVHs is not sufficient evidence that the original target was preserved.

The AAPM HDSS newsletter motivates the interoperability problem. The paper's new contribution is the linked experimental decomposition and reproducible results, not a claim that the volume effect was first discovered here. The public IHE listing still places HDSS under Public Comment at the source-check date; neither profile status nor a vendor roadmap establishes product implementation.

## Journal preparation

Use the current [Medical Physics author instructions](https://aapm.onlinelibrary.wiley.com/hub/journal/24734209/about/author-guidelines), checked 26 September 2026. The accompanying concept presentation begins with a concise requirements checklist. Journal rules override generic conference-paper templates. Plan for ten published pages including references, front matter, captions and any appendix; exact typesetting is a later check. The proposed five figures and two tables are our allocation, not a journal-imposed figure count. This is a Research Article, not a Dataset Article: the purpose is analysis and interpretation rather than dataset description alone.

## Questions and evidence

| Question / bounded claim | Current evidence | Main location | Remaining qualification |
|---|---|---|---|
| Does transfer change small target representations? | 24 paired synthetic targets, native/regular/HDSS and four Eclipse routes; actual Monaco subset | Figure 2; Table 1 | Name both geometric models; source-grid recovery is a distinct check |
| Does changed geometry alter readout at the same dose? | Common evaluator, unchanged fine dose in each pair; 480 observed planning-target states including Monaco | Figure 3; Table 2 | Descriptive target-level evidence on one anatomy; no patient-level inference |
| Can native DVH agreement conceal changed geometry? | 24 matched PTVs and 24 GTVs across three native TPS readouts; PTV13 example | Figure 4 | Full-route difference, not unique proof of an internal algorithm |
| Does planning on the returned target change the dose evaluated on the original target? | Four replans: two transfer routes × two margins; 24 PTVs per plan | Figure 5 | Repeat unchanged templates to quantify optimizer reproducibility |
| Does MR-linked geometry transfer add an effect? | 24 paired GTV geometries, four passive CT controls; evaluated on three fixed dose fields | Figure S1 | Shared registrations; resampling experiment, not registration-error assessment |

## Experimental design and primary estimand

The planned primary comparison is the **1-mm PTV plan**, because it directly represents planning on small margin-expanded targets. For every target and route, define ΔD98 as transferred-target D98 minus original-target D98 on the same original physical dose field using the common evaluator. The zero- and 2-mm plans are secondary size/margin scenarios. This primary/secondary ordering was chosen during concept development after reviewing the existing results; it is not preregistered.

One public CT/MR anatomy carries 24 synthetic GTVs. Nominal volume groups are 6.5 mm³ (4 spheres), 30 mm³ (4 spheres, 4 ellipsoids, 2 irregular objects) and 120 mm³ (the same 4/4/2 split). Native structures are stored on a 0.4-mm grid. CT/MR slice spacing is 1 mm, with 0.5-mm in-plane image spacing. Source grids are parallel or 30° oblique; target centres lie on or halfway between CT planes. Irregular objects exist only on the oblique grid. Thus size, shape, position and angle are not fully independent factors. The analytic nominal volumes are not substituted for the stored native references.

Three original plans use 0-, 1- and 2-mm margins. Regular and HDSS exports are assessed directly and after Eclipse Low/High import. RayStation receives the regular export for the native-DVH comparison. Monaco supplies 24 actual GTVs and 17/7 actual 1-/2-mm PTVs; other contours inferred by a rounding rule are excluded from this paper's principal analysis. These unequal groups should be compared on the matched available target subset, as well as being displayed with their own denominators.

All four replans were optimised in Elements, with the same nominal planning settings, on standard-return or HDSS→Eclipse High targets. They are not Eclipse, Monaco or RayStation optimization comparisons. The new dose is read on both its planning target and the original target. Two contrasts must remain separate: (i) same new dose, changed evaluation target; (ii) changed plan dose, same original target. Original fields are held fixed for the transfer experiment, but exported-dose resampling and independent dose-calculation differences are not thereby universally excluded.

## Reference representations and numerical validation

The existing geometry analysis compares native binary bodies and returned contour slabs. The complete-volume DVH analysis uses recovered source-grid surfaces for original/HDSS and declared polygon slabs for ordinary contours. These are different reference models: nonunity contour Dice can coexist with zero HDSS DVH change. Report this directly in the main Methods and captions. An exactly recovered source grid establishes encoding consistency, not independent receiver accuracy or an exact continuous anatomical boundary.

Integration is currently 0.05 mm; it does not create finer physical dose information. Existing selected-case refinement to 0.025 mm covers 19 target/plan cases and 150 paired D98 contrasts: median absolute change 0.0063 Gy, 95th percentile 0.0226 Gy, maximum 0.1249 Gy. Selection followed observed numerical sensitivity and is not universal convergence evidence. Refine the maximum and any headline result whose threshold/category changes. Include the numerical-sensitivity table in the supplement. The anatomy-free analytical sphere example supplies an exact D98 check independent of the original-image geometry.

The measured native readouts retain actual exported point sequences. Tests supporting a discrete-dose/fractional-volume RayStation model or a shape/interpolated-dose Eclipse model are model consistency evidence. Freeze choices of coordinates, shape convention and dose-field assignment before validation on withheld target families/settings; do not select models by fitting the same displayed curves. If assignment is fully metadata-driven, independently verify transforms and field support rather than implying a trained predictive model.

## Analysis and statistics

Report signed paired differences, medians, ranges and all-target plots. D98 is primary; Dmean, V20, volume difference and overlap are secondary. Counts at |ΔD98| ≥0.5 and ≥1.0 Gy are separate descriptive screens with explicit n; they are not endorsed safety limits. Never combine D98 and V20 with an OR rule for the headline outcome.

The unit is one deliberately constructed target under repeated routes, nested within one shared anatomical benchmark and shared plans. There are 24 target designs, not 480 independent cases or 96 independent replans. Avoid population-level p-values or bootstrap intervals that pretend these targets represent a random patient sample. Show paired route comparisons and within-design descriptive strata. Report full data for any retrospectively chosen extreme (PTV13), alongside all matched targets. Clinical outcome and population-risk claims are outside the study.

## Manuscript outline and space allocation

1. **Abstract and front matter (~0.5 page):** problem, purpose, fixed-dose design, one main quantitative result, bounded conclusion. Author/title information stays separate during review.
2. **Introduction (~0.75 page):** known small-target volume/DVH uncertainty; HDSS information retention; missing end-to-end separation; the three research questions. Newsletter and prior quantitative DVH papers provide context.
3. **Materials and Methods (~2.0 pages):** public-source preparation and synthetic targets; source-grid/contour representations; versions/import options; fixed-dose estimand; native readouts; four replans; numerical refinement; descriptive analysis and data governance.
4. **Results (~3.0 pages including figures/tables):** geometry first, fixed-dose effect second, native/common discrepancy third, replanning fourth. Primary 1-mm PTV results remain visible; other margins are sensitivity scenarios. No new causal claims are introduced in the Results.
5. **Discussion (~1.5 pages):** source information loss versus dose sampling; why apparent DVH agreement can mislead; reference-geometry evaluation of replans; comparison with previous analytical DVH work; workflow relevance; limited anatomy, reduced factor panel, model dependence, version specificity and optimizer variation.
6. **Conclusion and declarations (~0.5 page):** preserve source geometry and evaluate transfer separately from optimization; bounded to tested routes. Data/code availability, actual AI assistance, funding, conflicts and institutional ethics determination are completed from verified facts.
7. **References / layout reserve (~1.75 pages):** total target 10 published pages. Move full target tables, sensitivity cases and detailed recipes to supplements, not indispensable definitions.

## Main outputs and supplements

Main: five figures and two tables listed in `CAPTIONS.md`. Figure 4 includes both the extreme example and the complete matched PTV set. Table 2 shows the primary 1-mm result; its all-plan CSV is supplementary. Figures are regenerated from included numeric extracts, not screenshots of clinical systems.

Supplement: S1 all observed target-level data and native curve files; S2 MR-to-CT paired results; S3 anatomy-free analytical sampling generator and expected results; S4 numerical-refinement inventory and model-assignment checks; S5 machine/software/import-setting manifest and missing-data accounting. The present package supplies the numeric extracts, S1/S2 plots and analytical generator. Additional controls remain labelled pending until measured.

## Ethics, anonymization and open science

No local clinical cohort, real metastasis contours, patient images or clinical screenshots enter this concept release. The original benchmark anatomy is from Yao, Tan and Wang's public dataset; its live license is CC BY-NC 4.0 at the check date. Cite its provenance and modifications. Public availability and removal of identifiers do not themselves establish ethics exemption. Obtain the locally appropriate determination for secondary use of public human-derived images, then state its exact wording/status. No approval number or waiver is invented. The analytical supplement is wholly synthetic and contains no human-derived information.

The UKL presentation is for collaborators. Reviewer files omit our names, logos, email, local paths and identifying repository links. Vendor/software names and versions remain because they are methodological variables, not patient identities. A public GitHub release and a double-anonymized review bundle are distinct artifacts; publication on GitHub can make the study indirectly identifiable. If needed, agree the anonymous access mechanism with the editor. Preserve third-party source citations and applicable licenses.

Code is open under MIT in the existing project. Numeric benchmark extracts and resulting figures/tables are designated CC BY-NC 4.0; original CT/MR pixels are linked, not mirrored. Archive a frozen release with a new DOI only after final controls, then cite that version. A GitHub URL alone is not a newly minted archival DOI.

## Citation scaffold (verified sources)

1. Vögele R, Bosch W, Schadt C. High-Definition Structure Sets for Stereotactic Radiotherapy. AAPM Newsletter. 2024;49(5):21–22. [Original issue](https://www.aapm.org/pubs/newsletter/archive/4905.pdf). Motivation; not peer-reviewed validation of this benchmark.
2. Stanley DN, Covington EL, Liu H, et al. Accuracy of dose-volume metric calculation for small-volume radiosurgery targets. Medical Physics. 2021;48:1461–1468. [doi:10.1002/mp.14645](https://doi.org/10.1002/mp.14645). Analytical small-target DVH comparison; our addition is the linked transfer/replanning decomposition.
3. DICOM Standards Committee. PS3.3, C.8.8.6.4, Source Pixel Planes Characteristics. [Current standard](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.8.6.4.html). Geometry-grid semantics.
4. IHE Radiation Oncology. High-Definition Structure Set Content. [Profile status and document](https://profiles.ihe.net/RO/). Snapshot date 26 September 2026: listed under Public Comment.
5. Yao S, Tan Y, Wang J. A Paired Head CT-MRI Dataset for Cross-Modality Image Synthesis. Zenodo; 2025. [doi:10.5281/zenodo.17486320](https://doi.org/10.5281/zenodo.17486320). Anatomy provenance.

The ring-trial paper and dataset can motivate subsequent external validation, but their local reanalysis is outside this deliberately self-contained synthetic-target paper. No private vendor correspondence is presented as a published source or implementation guarantee.

## Independent outline review and minimal completion plan

An independent review confirmed the five-figure/two-table structure and requested: make the representation mismatch explicit; retain complete matched native results; avoid pseudoreplication; use the existing 0.025-mm checks; repeat unchanged optimization; validate any empirical method assignment on withheld configurations; and keep actual Monaco subsets distinct. These points are incorporated above. Review was performed with the available agent model because the skill's specified reviewer model was not available.

Before manuscript freeze:

- Repeat each unchanged original 1-/2-mm template at least once; keep inputs, objectives, normalization and stopping rules fixed. If variation matters, add repeats or keep optimization conclusions descriptive.
- Refine the remaining numerical extreme and screen threshold-borderline cases. Update figures only from the frozen recomputed table.
- Freeze geometric and dose-model choices; independently verify assignment or test withheld configurations.
- Confirm missing Monaco objects and compare available matched subsets. Do not fill them with inferred contours in main results.
- Record actual software builds/settings and current profile version; do not assume future releases behave like the tested versions.
- Confirm authorship, conflicts, source licensing and the local ethics-status wording; then freeze the reviewer archive and public release, and write the full manuscript.
