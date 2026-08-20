from __future__ import annotations

import joblib
from pathlib import Path

import pandas as pd

from src.eligibility import evaluate_eligibility
from src.features import build_fintech_features
from src.risk_score import risk_summary

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / 'models' / 'default_model.joblib'


def predict_default_probability(applicant: dict, loan: dict) -> float:
    """Use the trained model to estimate default probability from applicant and loan inputs."""
    model = joblib.load(MODEL_PATH)
    record = {
        'loan_amnt': float(loan.get('loan_amnt', 0) or 0),
        'annual_inc': float(applicant.get('annual_inc', 0) or 0),
        'dti': float(loan.get('dti', 0) or 0),
        'revol_util': float(applicant.get('revol_util', 0) or 0),
        'delinq_2yrs': float(applicant.get('delinq_2yrs', 0) or 0),
        'emp_length': float(applicant.get('emp_length', 0) or 0),
        'inq_last_6mths': float(applicant.get('inq_last_6mths', 0) or 0),
        'fico_range_low': float(applicant.get('fico_range_low', 0) or 0),
        'earliest_cr_line': '2015-01-01',
        'loan_status': 'Fully Paid',
        'issue_d': pd.Timestamp.now().strftime('%b-%Y'),
        'home_ownership': 'RENT',
        'grade': 'A',
        'sub_grade': 'A1',
        'purpose': 'debt_consolidation',
        'application_type': 'INDIVIDUAL',
        'term': '36 months',
    }

    df = pd.DataFrame([record])
    df = build_fintech_features(df)
    feature_columns = [
        'loan_amnt', 'annual_inc', 'loan_to_income_ratio', 'average_fico', 'dti',
        'revol_util', 'delinq_2yrs', 'employment_stability', 'utilization_category',
        'debt_burden_category', 'credit_history_length', 'inquiry_intensity',
        'delinquency_flag', 'income_category', 'loan_amount_category'
    ]
    present = [c for c in feature_columns if c in df.columns]
    probability = model.predict_proba(df[present])[0, 1]
    return float(probability)


def make_decision(applicant: dict, loan: dict, default_probability: float) -> dict:
    """Combine risk score, eligibility, and business rules into APPROVE / REVIEW / REJECT."""
    summary = risk_summary(default_probability)
    risk_score = summary['risk_score']
    risk_band = summary['risk_band']

    eligibility = evaluate_eligibility(
        applicant=applicant,
        loan=loan,
        risk_score=risk_score,
        default_probability=default_probability,
    )

    if not eligibility['eligible']:
        decision = 'REJECT'
    elif risk_band == 'Low Risk':
        decision = 'APPROVE'
    elif risk_band == 'Medium Risk':
        decision = 'REVIEW'
    elif risk_band == 'High Risk':
        decision = 'REVIEW'
    else:
        decision = 'REJECT'

    reasons = eligibility['reasons'][:]
    reasons.append(f'Risk band: {risk_band}')
    reasons.append(f'Default probability: {default_probability:.2%}')

    return {
        'decision': decision,
        'risk_score': risk_score,
        'risk_band': risk_band,
        'default_probability': default_probability,
        'eligible': eligibility['eligible'],
        'reasons': reasons,
    }
