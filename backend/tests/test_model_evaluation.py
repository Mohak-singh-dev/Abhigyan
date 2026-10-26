"""
Unit and integration tests for the AI Classifier Evaluation Pipeline.
Verifies split reproducibility, absence of data leakage, metric calculations,
and report generation with demo-only disclaimers.
"""

import json
import os
import numpy as np
import pytest

from ml.evaluate_model import (
    clean_text,
    compute_distribution,
    evaluate_end_to_end,
    evaluate_task,
    format_confusion_matrix_ascii,
    get_stratified_split,
    load_dataset,
)


def test_load_dataset_valid():
    """Verify training_data.csv loads properly with all required columns."""
    rows = load_dataset()
    assert len(rows) >= 150
    required = {"title", "description", "category", "bureau", "priority"}
    assert required.issubset(set(rows[0].keys()))


def test_clean_text_normalization():
    """Verify whitespace and edge cases are handled cleanly."""
    assert clean_text("  hello   world  \n\t") == "hello world"
    assert clean_text(None) == ""
    assert clean_text(123) == ""


def test_stratified_split_no_data_leakage():
    """Verify train and test splits have strictly zero overlap and valid proportions."""
    rows = load_dataset()
    split = get_stratified_split(rows, test_size=0.2, random_state=42)

    train_idx = set(split["train_idx"])
    test_idx = set(split["test_idx"])

    # Strict zero data leakage
    assert train_idx.isdisjoint(test_idx), "Data leakage: train and test indices overlap!"
    assert len(train_idx) + len(test_idx) == len(rows)

    # Stratification check: exactly 4 samples per category in 20% of 20 samples
    test_cat_dist = compute_distribution(split["test_cat"])
    assert len(test_cat_dist) == 9
    for cat, count in test_cat_dist.items():
        assert count == 4, f"Category {cat} should have exactly 4 test samples under stratified 20% split, got {count}"


def test_stratified_split_reproducibility():
    """Verify that split is 100% deterministic with fixed random_state."""
    rows = load_dataset()
    split1 = get_stratified_split(rows, test_size=0.2, random_state=42)
    split2 = get_stratified_split(rows, test_size=0.2, random_state=42)

    assert split1["train_idx"] == split2["train_idx"]
    assert split1["test_idx"] == split2["test_idx"]


def test_evaluate_task_arithmetic():
    """Verify precision, recall, accuracy, and confusion matrix arithmetic."""
    y_true = ["A", "A", "B", "B", "C"]
    y_pred = ["A", "B", "B", "B", "C"]
    classes = ["A", "B", "C"]

    res = evaluate_task(y_true, y_pred, "Test Task", classes)

    # Overall accuracy: 4 / 5 = 0.8
    assert res["accuracy"] == 0.8
    assert res["per_class"]["A"]["precision"] == 1.0  # 1 true A predicted, 0 false A
    assert res["per_class"]["A"]["recall"] == 0.5     # 1 out of 2 true A predicted
    assert res["per_class"]["C"]["f1_score"] == 1.0

    # Confusion matrix checks
    cm = np.array(res["confusion_matrix"])
    assert np.trace(cm) == 4
    assert np.sum(cm) == 5
    # Row sums equal ground truth support
    assert np.sum(cm[0]) == 2  # class A support
    assert np.sum(cm[1]) == 2  # class B support
    assert np.sum(cm[2]) == 1  # class C support


def test_format_confusion_matrix_ascii():
    """Verify confusion matrix ASCII rendering produces readable tabular output."""
    cm = np.array([[2, 1], [0, 3]])
    ascii_table = format_confusion_matrix_ascii(["Cat1", "Cat2"], cm)
    assert "Actual \\ Pred" in ascii_table
    assert "Cat1" in ascii_table
    assert "Cat2" in ascii_table


def test_evaluate_end_to_end_outputs_and_disclaimer():
    """Verify full pipeline runs end-to-end and saves valid report artifacts."""
    report = evaluate_end_to_end()

    # Core keys
    assert "category_evaluation" in report
    assert "priority_evaluation" in report
    assert "hybrid_bureau_evaluation" in report
    assert "confidence_analysis" in report
    assert "manual_review_statistics" in report
    assert "disclaimer" in report
    assert "limitations" in report

    # Demo-only disclaimer check
    assert "PROTOTYPE / DEMO-ONLY" in report["disclaimer"]
    assert len(report["limitations"]) >= 3

    # Check file artifacts
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "ml", "artifacts", "evaluation_report.json")
    md_path = os.path.join(base_dir, "ml", "artifacts", "evaluation_report.md")

    assert os.path.exists(json_path)
    assert os.path.exists(md_path)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["category_evaluation"]["accuracy"] == report["category_evaluation"]["accuracy"]

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    assert "Abhigyan AI Complaint Classifier: End-to-End Evaluation Report" in md_text
    assert "PROTOTYPE / DEMO-ONLY BENCHMARK" in md_text
