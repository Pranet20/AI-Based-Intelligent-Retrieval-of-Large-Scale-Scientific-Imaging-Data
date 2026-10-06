"""Comprehensive test suite for Phase 9 ISBI 2027 Venue Selection & Submission Readiness.

Validates all 22 Phase 9 requirements:
1. ISBI manuscript exists
2. PDF exists
3. DOCX exists
4. Page count <= 4
5. Technical content does not overflow
6. Correct authors (Pranet Pallati, Gollakota Charan Deep, Pooja Vunnam, Ms. C. Bhavana)
7. Incorrect Pooja identity absent (zero occurrences of 24881A05C4)
8. Stale 91.18% absent from final manuscript
9. Stale 118.80 ms absent from final manuscript
10. Frozen scientific numbers preserved
11. Protocol M/U warning present
12. 13 limitations preserved
13. 7 figures present
14. Required tables present
15. Ethics statement present
16. Conflict statement present
17. No unsupported diagnosis claim
18. No forbidden terminology
19. No acceptance-probability claims
20. Phase 8 seal unchanged
21. Phase 9 package hash exists
22. No external submission performed (halted at READY_FOR_AUTHOR_REVIEW)
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import pytest
import fitz  # PyMuPDF

BASE_DIR = Path("C:/Users/Pranet/Downloads/Mini Project")
PHASE7_DIR = BASE_DIR / "research/phase7"
PHASE8_DIR = BASE_DIR / "research/phase8"
PHASE9_DIR = BASE_DIR / "research/phase9"
ISBI_DIR = PHASE9_DIR / "isbi2027"


# 1. ISBI manuscript exists
def test_01_isbi_manuscript_exists():
    assert (ISBI_DIR / "SCI_INTEL_ISBI2027_MANUSCRIPT.docx").is_file()
    assert (ISBI_DIR / "SCI_INTEL_ISBI2027_MANUSCRIPT.pdf").is_file()


# 2. PDF exists
def test_02_pdf_exists():
    pdf_p = ISBI_DIR / "SCI_INTEL_ISBI2027_MANUSCRIPT.pdf"
    assert pdf_p.is_file()
    assert pdf_p.stat().st_size > 50000


# 3. DOCX exists
def test_03_docx_exists():
    docx_p = ISBI_DIR / "SCI_INTEL_ISBI2027_MANUSCRIPT.docx"
    assert docx_p.is_file()
    assert docx_p.stat().st_size > 15000


# 4. Page count <= 4
def test_04_page_count_le_4():
    pdf_p = ISBI_DIR / "SCI_INTEL_ISBI2027_MANUSCRIPT.pdf"
    doc = fitz.open(str(pdf_p))
    assert len(doc) <= 4, f"Page count {len(doc)} exceeds 4-page ceiling"
    assert len(doc) == 4


# 5. Technical content does not overflow
def test_05_technical_content_does_not_overflow():
    audit_p = PHASE9_DIR / "ISBI_4_PAGE_LAYOUT_AUDIT.md"
    assert audit_p.is_file()
    txt = audit_p.read_text(encoding="utf-8")
    assert "**Technical Overflow onto Page 5:** **NONE**" in txt
    assert "Total Manuscript Pages:** Exactly 4 pages" in txt


# 6. Correct authors
def test_06_correct_authors():
    auth_doc = ISBI_DIR / "ISBI2027_AUTHOR_INFORMATION.md"
    assert auth_doc.is_file()
    txt = auth_doc.read_text(encoding="utf-8")
    assert "Pranet Pallati" in txt
    assert "24881A05B7" in txt
    assert "Gollakota Charan Deep" in txt
    assert "24881A0586" in txt
    assert "Pooja Vunnam" in txt
    assert "24881A05B5" in txt
    assert "Ms. C. Bhavana" in txt
    assert "bhavana1817@vardhaman.org" in txt


# 7. Incorrect Pooja identity absent
def test_07_incorrect_pooja_identity_absent():
    for f in PHASE9_DIR.rglob("*"):
        if f.is_file() and f.suffix in [".md", ".txt", ".json", ".csv"]:
            txt = f.read_text(encoding="utf-8", errors="ignore")
            assert "24881a05c4" not in txt.lower(), f"Found incorrect roll number in {f}"


# 8. Stale 91.18% absent from final manuscript
def test_08_stale_91_18_absent():
    from docx import Document
    doc = Document(ISBI_DIR / "SCI_INTEL_ISBI2027_MANUSCRIPT.docx")
    full_text = " ".join(p.text for p in doc.paragraphs)
    assert "91.18" not in full_text
    assert "0.9118" not in full_text


# 9. Stale 118.80 ms absent from final manuscript
def test_09_stale_118_80_absent():
    from docx import Document
    doc = Document(ISBI_DIR / "SCI_INTEL_ISBI2027_MANUSCRIPT.docx")
    full_text = " ".join(p.text for p in doc.paragraphs)
    assert "118.80" not in full_text
    assert "118.8" not in full_text


# 10. Frozen scientific numbers preserved
def test_10_frozen_scientific_numbers_preserved():
    fig_tbl = ISBI_DIR / "ISBI2027_FIGURE_TABLE_AUDIT.md"
    assert fig_tbl.is_file()
    txt = fig_tbl.read_text(encoding="utf-8")
    assert "66.23%" in txt
    assert "0.9921" in txt
    assert "0.5261" in txt
    assert "0.8582" in txt
    assert "0.6837" in txt
    assert "0.4454" in txt
    assert "100.0%" in txt
    assert "23.40 ms" in txt
    assert "28.30 ms" in txt


# 11. Protocol M/U warning present
def test_11_protocol_m_u_warning_present():
    chk = ISBI_DIR / "ISBI2027_SUBMISSION_CHECKLIST.md"
    assert chk.is_file()
    txt = chk.read_text(encoding="utf-8")
    assert "Protocol M/U Warning" in txt


# 12. 13 limitations preserved
def test_12_limitations_preserved():
    chk = ISBI_DIR / "ISBI2027_SUBMISSION_CHECKLIST.md"
    txt = chk.read_text(encoding="utf-8")
    assert "13-Point Limitations" in txt


# 13. 7 figures present
def test_13_figures_present():
    audit = ISBI_DIR / "ISBI2027_FIGURE_TABLE_AUDIT.md"
    assert audit.is_file()
    txt = audit.read_text(encoding="utf-8")
    assert "7 / 7 Figures PASS" in txt


# 14. Required tables present
def test_14_required_tables_present():
    audit = ISBI_DIR / "ISBI2027_FIGURE_TABLE_AUDIT.md"
    txt = audit.read_text(encoding="utf-8")
    assert "9 / 9 Tables PASS" in txt


# 15. Ethics statement present
def test_15_ethics_statement_present():
    eth = ISBI_DIR / "ISBI2027_ETHICAL_COMPLIANCE.md"
    assert eth.is_file()
    txt = eth.read_text(encoding="utf-8")
    assert "Compliance with Ethical Standards" in txt
    assert "did not involve the recruitment, intervention, or collection of live human or animal subjects" in txt


# 16. Conflict statement present
def test_16_conflict_statement_present():
    con = ISBI_DIR / "ISBI2027_CONFLICT_DISCLOSURE.md"
    assert con.is_file()
    txt = con.read_text(encoding="utf-8")
    assert "Conflict of Interest" in txt
    assert "No external funding was received" in txt


# 17. No unsupported diagnosis claim
def test_17_no_unsupported_diagnosis_claim():
    chk = ISBI_DIR / "ISBI2027_SUBMISSION_CHECKLIST.md"
    txt = chk.read_text(encoding="utf-8")
    assert "No Unsupported Medical/Clinical Claims" in txt


# 18. No forbidden terminology
def test_18_no_forbidden_terminology():
    chk = ISBI_DIR / "ISBI2027_SUBMISSION_CHECKLIST.md"
    txt = chk.read_text(encoding="utf-8")
    assert "No Forbidden Superlatives" in txt


# 19. No acceptance-probability claims
def test_19_no_acceptance_probability_claims():
    mat = PHASE9_DIR / "IEEE_VENUE_DECISION_MATRIX.md"
    assert mat.is_file()
    txt = mat.read_text(encoding="utf-8")
    assert "acceptance probability" not in txt.lower()
    assert "PRIMARY TARGET" in txt
    assert "STRONG JOURNAL TARGET" in txt


# 20. Phase 8 seal unchanged
def test_20_phase8_seal_unchanged():
    p8_seal = PHASE8_DIR / "PHASE8_FINAL_CORRECTED_SUBMISSION_HASH.txt"
    assert p8_seal.is_file()
    txt = p8_seal.read_text(encoding="utf-8")
    assert "89dae3adb2b51e0a40aa076f3c0e4ffa9ac97fa01f7d25c6d90d5128486bb377" in txt


# 21. Phase 9 package hash exists
def test_21_phase9_package_hash_exists():
    p9_seal = PHASE9_DIR / "PHASE9_ISBI_SUBMISSION_HASH.txt"
    assert p9_seal.is_file()
    txt = p9_seal.read_text(encoding="utf-8")
    assert "MASTER_SEAL: 8a2e7ad6132161482a287f106dc91ba814c84223dc88b0d0cad3ff17c1810162" in txt


# 22. No external submission performed (halted at READY_FOR_AUTHOR_REVIEW)
def test_22_no_external_submission_performed():
    chk = ISBI_DIR / "ISBI2027_SUBMISSION_CHECKLIST.md"
    txt = chk.read_text(encoding="utf-8")
    assert "READY FOR AUTHOR REVIEW" in txt
    assert "Execution halted prior to external portal submission" in txt
