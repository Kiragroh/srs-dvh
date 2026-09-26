# Structured abstract — concept-stage draft

Not a submission-ready abstract. Existing numeric results are shown; the final abstract must be updated after the numerical and optimizer controls specified in PAPER_PLAN.md.

**Background:** Small-target structure transfer can change the represented target, while native dose-volume histograms (DVHs) also depend on reconstruction and sampling. Agreement between displayed DVHs therefore may not establish preservation of the source geometry.

**Purpose:** To distinguish geometry-dependent fixed-dose effects, native-versus-common DVH discrepancies, and the consequences of replanning on transferred targets using an openly documented technical benchmark.

**Methods:** Twenty-four synthetic targets of three nominal volume groups were placed on public CT/MR anatomy. Three original plans used 0-, 1- and 2-mm margins. Regular and high-definition structure-set exports were assessed directly and after selected treatment-planning-system import routes. A common complete-volume evaluator compared each transferred target with its original on an unchanged physical dose field. Native DVHs were retained separately. Four source-system replans were evaluated on both their planning targets and original targets. Analyses were paired and descriptive; repeated targets were not treated as independent patients. The proposed primary analysis concerns the 1-mm PTV plan.

**Results:** In the current 1-mm analysis, regular export produced a median D98 change of −0.247 Gy (range −0.738 to −0.058 Gy); 6/24 targets had an absolute change of at least 0.5 Gy. Following the HDSS-to-Eclipse High route, the corresponding median was −0.419 Gy (−2.150 to −0.109 Gy), with 10/24 targets meeting that screen. Recovery of the original HDSS source-grid surface gave zero change as an encoding consistency check. Native and common-evaluator comparisons differed: native agreement could coexist with altered geometry. Replanning results remain descriptive pending unchanged-template repeat controls.

**Conclusions:** This benchmark supports evaluating structure transfer and native dose-volume readout as distinct checks, and evaluating replanned dose on the original target. Findings are specific to one anatomical benchmark, the synthetic target panel, declared reference representations and tested software settings. They do not establish clinical outcome effects or unique proprietary DVH algorithms.
