# PHASE 4 OUT-OF-DISTRIBUTION (OOD) SCREENING AUDIT REPORT
**Project**: AI-Based Intelligent Retrieval and Quality-Aware Curation of Scientific Microscopy Images  
**Evaluation Standard**: IEEE Research Reproducibility & Scientific Integrity Standards  
**Status**: PASS (With Strict Cross-Domain Interpretation Standards)

---

## 1. Experimental Protocol & In-Distribution vs. Out-of-Distribution Cohorts

To evaluate embedding-space out-of-distribution (OOD) screening, the system evaluated distance metrics against an external materials microscopy corpus:

- **In-Distribution (ID) Reference Set**: HCCI training split ($N = 427$ micrographs, high-carbon steel alloys).
- **Out-of-Distribution (OOD) Test Cohort**: Carinthia SEM dataset subset ($N = 100$ randomly selected micrographs using deterministic seed 42).
- **Novelty Metric**: Mean Euclidean distance to the $k = 5$ nearest neighbors in $\ell_2$-normalized foundation model embedding space.
- **Data Isolation Audit**: Confirmed zero Carinthia images were utilized during model training, representation adaptation, or split selection.

---

## 2. Empirical Results

| Metric | Measured Value | Standard Interpretation |
|:---|:---:|:---|
| **AUROC** | **1.0000** | Perfect empirical separability between HCCI and Carinthia |
| **AUPRC** | **1.0000** | Perfect precision-recall under test balance |
| **FPR @ 95% TPR** | **0.0000** | Zero false positive HCCI micrographs at 95% Carinthia detection |

---

## 3. Critical Scientific Context & Disclaimers

While the metrics reflect complete separability ($\text{AUROC} = 1.0000$), scientific integrity dictates contextualizing this result honestly rather than overclaiming generalized anomaly detection:

### Standardized Authoritative Declaration:
> *"The evaluated Carinthia subset was completely separable from the HCCI reference distribution under the selected novelty score."*
> 
> *"This is evidence of controlled cross-domain distribution-shift detection, not general open-world OOD performance."*

### Scientific Factors Governing Separation:
1. **Gross Domain Shift**: HCCI micrographs consist exclusively of martensitic/austenitic steel alloys with characteristic microstructural morphology, whereas Carinthia comprises heterogeneous multi-mineral, geological, and ceramic SEM micrographs.
2. **Feature Distance Mechanics**: Foundation model embeddings easily separate distinct material classes. Separating geological rock specimens from polished steel is a coarse cross-domain screening task, not subtle defect detection.
3. **No Claim of Open-World Competence**: This result must not be interpreted as proving the system can detect subtle micro-defects or unseen metallurgical phases within HCCI steels with 100% reliability.

---

## 4. Final Determination
**OOD Audit Result**: **PASS**  
AUROC ($1.0000$) is preserved as authentic empirical evidence, accompanied by strict and transparent scientific disclaimers.
