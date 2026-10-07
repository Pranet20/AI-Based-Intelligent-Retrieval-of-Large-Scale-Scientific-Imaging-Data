# Scientific & Methodological Limitations Map

The manuscript must include an explicit, unvarnished discussion of scientific and practical limitations in Section IX.

---

## 1. Dataset & Benchmark Limitations

1. **Overlapping Specimen Classes:**
   - In the HCCI benchmark (774 micrographs), identical AISI 52100 metallurgical specimen classes (As-Cast, Water-Quenched, Air-Cooled) occur across train, validation, and test splits under varying beam voltages (5–20 kV) and detectors.
   - The benchmark evaluates **cross-acquisition and cross-instrument retrieval robustness** under known morphology, **not** generalization to unseen metallurgical alloys or arbitrary biological specimens.

2. **Synthetic Quality Artifacts:**
   - Quality screening (AUROC = 0.8582) and localization (IoU = 0.4454) were evaluated on controlled synthetic augmentations (2,750 micrographs generated from 250 pristine parents across 11 artifact classes).
   - Controlled perturbations cannot fully model the full complexity of physical optical misalignments, chamber contamination, or sample charging occurring in physical microscopy laboratories.

3. **Carinthia Defect SEM Screening:**
   - Perfect screening metrics on Carinthia SEM ($N=100$, AUROC = 1.0000) reflect cross-domain distribution-shift screening between different material domains, not open-world microscopic defect detection within a single modality.

4. **Evidence Cohort Scope:**
   - 100% valid evidence availability applies strictly to the evaluated $N=55$ matched query cohort where complete multi-voltage and multi-detector capture series existed. It must not be generalized to unstructured, incomplete repositories.

---

## 2. Model & Representation Limitations

1. **No Learned Representation Fusion:**
   - SCI-INTEL implements architectural separation (DINOv2 for screening; Phase 4 for retrieval) rather than a joint learned representation or multimodal fusion head.

2. **Calibration & Abstention Burden:**
   - Standard temperature scaling leaves non-trivial calibration error (ECE = 0.3333, Brier = 0.4821).
   - High selective accuracy (100%) requires high abstention rates (90.27%), demonstrating that automated screening cannot operate autonomously without expert oversight.

3. **Spatial Localization Fidelity:**
   - Attention-derived localization achieves moderate overlap (Macro IoU = 0.4454, Dice = 0.5103).
   - Visual bounding boxes must be treated as indicative attention highlights, not precise physical defect boundaries.

---

## 3. Deployment & Operational Limitations

1. **No Clinical or Prospective Laboratory Validation:**
   - The system has not undergone clinical prospective trials or live deployment in a certified material-testing facility.
   - All evaluations are retrospective computational benchmarks.

2. **Human-in-the-Loop Requirement:**
   - All automated classifications, duplicate detections, and corrective suggestions are purely recommendations. Curatorial final disposition remains strictly with human researchers.
