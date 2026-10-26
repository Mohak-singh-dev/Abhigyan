"""
Tests for AI-Based Complaint Classifier Service (Task 2).
Validates:
- Valid complaint text inference
- Empty and whitespace-only inputs
- Confidence threshold and manual review triggers
- Missing and corrupted model artifact resilience
- Output conformity to valid categories, bureaus, and priorities
"""

import os
import tempfile
import pytest
from app.services.ai_classifier import (
    classify_complaint,
    _ModelCache,
    VALID_BUREAUS,
    VALID_PRIORITIES,
)

VALID_CATEGORIES = {
    "Fee Regulation",
    "Faculty Norms",
    "Infrastructure",
    "Admission Irregularity",
    "Certificate Delay",
    "Curriculum",
    "Unapproved Courses",
    "Harassment & Ragging",
    "Skill Certification",
}


def test_valid_complaint_classification():
    """Verify that clear, domain-specific complaint text produces structured output."""
    title = "Illegal capitation fee and non-refund of caution money"
    description = "The college is demanding cash donations and refusing to refund hostel caution deposit."
    
    result = classify_complaint(title=title, description=description)
    assert result is not None
    assert result["status"] == "success"
    assert result["category"] in VALID_CATEGORIES
    assert result["bureau"] in VALID_BUREAUS
    assert result["priority"] in VALID_PRIORITIES
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["priority_confidence"] <= 1.0
    assert isinstance(result["needs_manual_review"], bool)
    assert "advisory_notice" in result
    assert result["model_version"] is not None


def test_empty_or_whitespace_input():
    """Verify that empty, none, or whitespace-only inputs are safely handled without crash."""
    test_cases = [
        ("", ""),
        ("   ", "   \t\n"),
        ("", "   "),
        ("Valid Title", "   "),
        (None, None),
    ]

    for title, desc in test_cases:
        res = classify_complaint(title=title, description=desc)
        assert res is not None
        if not (title or "").strip() and not (desc or "").strip():
            assert res["status"] == "invalid_input"
            assert res["needs_manual_review"] is True
            assert res["confidence"] == 0.0
            assert "empty_input" in res["review_reasons"]
        else:
            # At least one non-empty field should attempt classification
            assert res["status"] in ("success", "unavailable")


def test_high_confidence_threshold_triggers_manual_review():
    """Verify that setting an unreachable confidence threshold flags manual review."""
    title = "Syllabus not completed by department"
    description = "Only one unit taught before end semester exams."
    
    # 0.999 threshold forces manual review
    result = classify_complaint(title=title, description=description, confidence_threshold=0.999)
    assert result is not None
    assert result["needs_manual_review"] is True
    assert any("low_category_confidence" in reason for reason in result["review_reasons"])


def test_missing_model_artifacts_resilience():
    """Verify that if artifacts directory does not exist, service returns unavailable without crash."""
    non_existent_dir = os.path.join(tempfile.gettempdir(), "non_existent_ai_artifacts_dir_998877")
    result = classify_complaint(
        title="Severe ragging in campus",
        description="Freshers beaten in hostel.",
        artifacts_dir=non_existent_dir
    )
    assert result is not None
    assert result["status"] == "unavailable"
    assert result["category"] is None
    assert result["needs_manual_review"] is True
    assert result["confidence"] == 0.0


def test_corrupted_model_artifacts_resilience():
    """Verify that corrupted/unreadable artifact files do not crash the service."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create dummy corrupted files
        for fname in ["vectorizer.joblib", "category_model.joblib", "priority_model.joblib"]:
            with open(os.path.join(temp_dir, fname), "w") as f:
                f.write("corrupted non-pickle binary garbage")

        cache = _ModelCache(artifacts_dir=temp_dir)
        loaded = cache.load()
        assert loaded is False
        assert cache.load_failed is True
        assert cache.load_error is not None

        # classify_complaint with corrupted artifacts dir
        result = classify_complaint(
            title="Lab equipment missing",
            description="Computers broken in CAD lab.",
            artifacts_dir=temp_dir
        )
        assert result is not None
        assert result["status"] == "unavailable"
        assert result["needs_manual_review"] is True


def test_output_schema_advisory_notice():
    """Verify advisory notice is always included and matches ethical AI guidance."""
    result = classify_complaint("Hostel ragging", "Seniors harassed juniors")
    assert "advisory_notice" in result
    assert "advisory" in result["advisory_notice"].lower()
    assert "AICTE" in result["advisory_notice"]


def test_category_and_bureau_validity_across_categories():
    """Verify prediction categories and bureaus fall into expected allowable enumerations."""
    samples = [
        ("Fake unapproved university degree offered", "Running unauthorized engineering diploma."),
        ("Sexual harassment by professor", "Teacher harassed student during viva in office."),
        ("Pragati scholarship not credited", "Second year scholarship stipend pending for months."),
        ("Broken roof and waterlogging in chemistry lab", "Plumbing broken and ceiling collapsed.")
    ]
    for title, desc in samples:
        res = classify_complaint(title=title, description=desc)
        assert res["category"] in VALID_CATEGORIES
        assert res["bureau"] in VALID_BUREAUS
        assert res["priority"] in VALID_PRIORITIES
