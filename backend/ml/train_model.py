"""
Model training pipeline for AI-Based Complaint Classification.
Uses TF-IDF Vectorization and Logistic Regression from scikit-learn.

Trained on synthetic complaint data for prototyping and local development.
Artifacts are saved locally to `backend/ml/artifacts/`.
"""

import csv
import json
import logging
import os
import sys
from datetime import datetime, timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
import joblib

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Configurable default Category to Bureau mapping
DEFAULT_CATEGORY_TO_BUREAU = {
    "Fee Regulation": "PGRC",
    "Faculty Norms": "Approval",
    "Infrastructure": "Approval",
    "Admission Irregularity": "Approval",
    "Certificate Delay": "Academic",
    "Curriculum": "Academic",
    "Unapproved Courses": "Approval",
    "Harassment & Ragging": "PGRC",
    "Skill Certification": "SB",
}

# Categories with multiple possible Bureaus depending on specific context
MULTI_BUREAU_RULES = {
    "Fee Regulation": ["PGRC", "RB"],
    "Admission Irregularity": ["Approval", "RB"],
    "Harassment & Ragging": ["PGRC", "EO"],
    "Certificate Delay": ["Academic", "SB"],
}

VALID_BUREAUS = ["RB", "PGRC", "Approval", "Academic", "SB", "EO"]
VALID_PRIORITIES = ["Critical", "High", "Medium", "Low"]

def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return " ".join(text.strip().split())

def train_and_evaluate(
    data_path: str = "backend/ml/training_data.csv",
    output_dir: str = "backend/ml/artifacts"
):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Training data not found at {data_path}")

    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Loading training data from {data_path}...")
    with open(data_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if len(rows) < 50:
        logger.warning(
            "Dataset is very small (<50 samples). Model generalization will be limited. "
            "Metrics may show high variance."
        )

    required_cols = {"title", "description", "category", "bureau", "priority"}
    fieldnames = set(rows[0].keys()) if rows else set()
    if not required_cols.issubset(fieldnames):
        raise ValueError(f"Dataset missing required columns. Expected {required_cols}, found {fieldnames}")

    # Combine title and description
    texts = [
        f"{preprocess_text(r['title'])} {preprocess_text(r['description'])}"
        for r in rows
    ]
    categories = [r["category"] for r in rows]
    priorities = [r["priority"] for r in rows]
    bureaus = [r["bureau"] for r in rows]

    logger.info(f"Total samples: {len(texts)}")
    logger.info(f"Unique categories ({len(set(categories))}): {sorted(list(set(categories)))}")
    logger.info(f"Unique priorities ({len(set(priorities))}): {sorted(list(set(priorities)))}")
    logger.info(f"Unique bureaus ({len(set(bureaus))}): {sorted(list(set(bureaus)))}")

    # Split dataset reproducibly with stratification on category
    test_size = 0.2 if len(rows) >= 50 else 0.1
    (
        train_texts, test_texts,
        train_cat, test_cat,
        train_prio, test_prio,
        train_bur, test_bur
    ) = train_test_split(
        texts, categories, priorities, bureaus,
        test_size=test_size,
        random_state=42,
        stratify=categories
    )

    logger.info(f"Train samples: {len(train_texts)}, Test samples: {len(test_texts)}")

    # 1. TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
        min_df=1
    )
    X_train = vectorizer.fit_transform(train_texts)
    X_test = vectorizer.transform(test_texts)

    # 2. Category Classifier
    category_model = LogisticRegression(
        max_iter=1000,
        C=1.0,
        solver="lbfgs",
        random_state=42
    )
    category_model.fit(X_train, train_cat)
    cat_preds = category_model.predict(X_test)
    cat_acc = accuracy_score(test_cat, cat_preds)
    cat_report = classification_report(test_cat, cat_preds, output_dict=True, zero_division=0)

    logger.info(f"Category Test Accuracy: {cat_acc:.4f}")
    print("\n=== Category Classification Report ===")
    print(classification_report(test_cat, cat_preds, zero_division=0))

    # 3. Priority Classifier
    priority_model = LogisticRegression(
        max_iter=1000,
        C=1.0,
        solver="lbfgs",
        random_state=42
    )
    priority_model.fit(X_train, train_prio)
    prio_preds = priority_model.predict(X_test)
    prio_acc = accuracy_score(test_prio, prio_preds)
    prio_report = classification_report(test_prio, prio_preds, output_dict=True, zero_division=0)

    logger.info(f"Priority Test Accuracy: {prio_acc:.4f}")
    print("\n=== Priority Classification Report ===")
    print(classification_report(test_prio, prio_preds, zero_division=0))

    # 4. Bureau Classifier (trained on dataset as auxiliary predictor alongside mapping)
    bureau_model = LogisticRegression(
        max_iter=1000,
        C=1.0,
        solver="lbfgs",
        random_state=42
    )
    bureau_model.fit(X_train, train_bur)
    bur_preds = bureau_model.predict(X_test)
    bur_acc = accuracy_score(test_bur, bur_preds)
    bur_report = classification_report(test_bur, bur_preds, output_dict=True, zero_division=0)

    logger.info(f"Bureau Test Accuracy: {bur_acc:.4f}")
    print("\n=== Bureau Classification Report ===")
    print(classification_report(test_bur, bur_preds, zero_division=0))

    # Save artifacts using joblib
    vectorizer_path = os.path.join(output_dir, "vectorizer.joblib")
    cat_model_path = os.path.join(output_dir, "category_model.joblib")
    prio_model_path = os.path.join(output_dir, "priority_model.joblib")
    bur_model_path = os.path.join(output_dir, "bureau_model.joblib")
    metadata_path = os.path.join(output_dir, "metadata.json")

    joblib.dump(vectorizer, vectorizer_path)
    joblib.dump(category_model, cat_model_path)
    joblib.dump(priority_model, prio_model_path)
    joblib.dump(bureau_model, bur_model_path)

    metadata = {
        "model_version": "prototype-v1.0.0",
        "model_type": "TF-IDF + LogisticRegression",
        "dataset_type": "synthetic_prototype",
        "status": "prototype",
        "advisory_notice": "AI classification is advisory only and does NOT constitute an official AICTE decision.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_training_samples": len(texts),
        "train_samples": len(train_texts),
        "test_samples": len(test_texts),
        "categories": sorted(list(category_model.classes_)),
        "priorities": sorted(list(priority_model.classes_)),
        "bureaus": sorted(list(bureau_model.classes_)),
        "category_to_bureau_default": DEFAULT_CATEGORY_TO_BUREAU,
        "multi_bureau_rules": MULTI_BUREAU_RULES,
        "metrics": {
            "category_accuracy": cat_acc,
            "category_macro_f1": cat_report["macro avg"]["f1-score"],
            "priority_accuracy": prio_acc,
            "priority_macro_f1": prio_report["macro avg"]["f1-score"],
            "bureau_accuracy": bur_acc,
            "bureau_macro_f1": bur_report["macro avg"]["f1-score"],
        },
        "limitations": [
            "Trained on synthetic complaint examples for prototype evaluation.",
            "Probability output represents model confidence, not calibrated real-world certainty.",
            "Categories with complex multi-bureau overlaps require manual officer review.",
            "Domain vocabulary shifts over time require periodic retraining."
        ]
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Artifacts successfully saved to {output_dir}")
    logger.info(f"Metadata saved to {metadata_path}")
    return metadata

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(base_dir, "ml", "training_data.csv")
    out_dir = os.path.join(base_dir, "ml", "artifacts")
    train_and_evaluate(data_file, out_dir)
