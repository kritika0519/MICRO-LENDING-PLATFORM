from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, classification_report,
                             confusion_matrix, f1_score, precision_recall_curve, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.features import build_fintech_features, select_model_features
from src.etl_pipeline import build_customer_table, build_default_flag, build_loan_table, clean_raw_dataset, standardize_columns

MODEL_PATH = ROOT_DIR / 'models' / 'default_model.joblib'
EVALUATION_DIR = ROOT_DIR / 'data' / 'model_evaluation'


def sample_training_data(sample_size: int = 50000) -> pd.DataFrame:
    """Use a reproducible random sample so status distribution is not time-window biased."""
    raw_path = ROOT_DIR / 'lendingLoan zip' / 'loan.csv'
    required_columns = {
        'id', 'member_id', 'loan_amnt', 'funded_amnt', 'term', 'int_rate', 'installment',
        'grade', 'sub_grade', 'purpose', 'title', 'issue_d', 'loan_status', 'dti',
        'annual_inc', 'emp_length', 'home_ownership', 'earliest_cr_line', 'fico_range_low',
        'fico_range_high', 'revol_util', 'delinq_2yrs', 'inq_last_6mths', 'inq_last_12m', 'inq_fi'
    }
    raw = pd.read_csv(raw_path, usecols=lambda column: column in required_columns, low_memory=False)
    raw = raw.sample(n=min(sample_size, len(raw)), random_state=42)
    raw = standardize_columns(raw)
    raw = build_default_flag(raw)

    customer = build_customer_table(raw)
    loan = build_loan_table(raw)
    merged = loan.merge(customer, on='member_id', how='left', suffixes=('_loan', '_customer'))
    return merged


def build_model_pipeline(X: pd.DataFrame, estimator=None) -> Pipeline:
    numeric_cols = X.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = [c for c in X.columns if c not in numeric_cols]

    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer([
        ('num', numeric_transformer, numeric_cols),
        ('cat', categorical_transformer, categorical_cols)
    ])

    model = estimator if estimator is not None else RandomForestClassifier(
        n_estimators=200, max_depth=8, random_state=42, class_weight='balanced'
    )

    return Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])


def evaluate_model(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> tuple[dict, pd.DataFrame]:
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_prob),
        'average_precision': average_precision_score(y_test, y_prob),
    }
    matrix = confusion_matrix(y_test, y_pred)
    matrix_frame = pd.DataFrame(matrix, index=['actual_0', 'actual_1'], columns=['predicted_0', 'predicted_1'])
    return metrics, matrix_frame


def train_final_model(sample_size: int = 100000):
    """Train model on a representative sample to avoid local memory overflow while preserving the real project workflow."""
    merged = sample_training_data(sample_size=sample_size)
    features_df = build_fintech_features(merged)
    X, y = select_model_features(features_df, target='default_flag')

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    estimators = {
        'logistic_regression': LogisticRegression(max_iter=500, class_weight='balanced'),
        'random_forest': RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, class_weight='balanced'),
        'gradient_boosting': GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42),
    }
    comparison = []
    trained_models = {}
    confusion_frames = {}
    for name, estimator in estimators.items():
        candidate = build_model_pipeline(X_train, estimator)
        candidate.fit(X_train, y_train)
        candidate_metrics, matrix_frame = evaluate_model(candidate, X_test, y_test)
        candidate_metrics['model'] = name
        comparison.append(candidate_metrics)
        trained_models[name] = candidate
        confusion_frames[name] = matrix_frame

    # Default detection is a risk-control task, so prioritize positive-class F1 and recall.
    comparison_frame = pd.DataFrame(comparison).sort_values(
        ['f1', 'recall', 'roc_auc'], ascending=False
    )
    selected_name = comparison_frame.iloc[0]['model']
    model = trained_models[selected_name]
    metrics = comparison_frame.iloc[0].drop('model').to_dict()

    print('Model metrics:')
    for key, value in metrics.items():
        print(f'{key}: {value:.4f}')

    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    comparison_frame.to_csv(EVALUATION_DIR / 'model_comparison.csv', index=False)
    confusion_frames[selected_name].to_csv(EVALUATION_DIR / 'confusion_matrix.csv')
    y_prob = model.predict_proba(X_test)[:, 1]
    precision_values, recall_values, thresholds = precision_recall_curve(y_test, y_prob)
    pd.DataFrame({'precision': precision_values, 'recall': recall_values}).to_csv(
        EVALUATION_DIR / 'precision_recall_curve.csv', index=False
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f'Model saved to: {MODEL_PATH}')

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, zero_division=0)
    print(report)
    return model, metrics


if __name__ == '__main__':
    train_final_model()
