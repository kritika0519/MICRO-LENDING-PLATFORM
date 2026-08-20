from __future__ import annotations

from typing import Iterable

import pandas as pd


def loan_to_income_ratio(df: pd.DataFrame) -> pd.Series:
    annual_income = pd.to_numeric(df['annual_inc'], errors='coerce').replace(0, float('nan'))
    loan_amount = pd.to_numeric(df['loan_amnt'], errors='coerce')
    return loan_amount / annual_income


def average_fico(df: pd.DataFrame) -> pd.Series:
    if 'fico_range_low' in df.columns and 'fico_range_high' in df.columns:
        return (df['fico_range_low'].fillna(0) + df['fico_range_high'].fillna(0)) / 2
    return pd.Series(0, index=df.index)


def credit_history_length(df: pd.DataFrame) -> pd.Series:
    if 'earliest_cr_line' in df.columns:
        values = pd.to_datetime(df['earliest_cr_line'], errors='coerce')
        if 'issue_d' in df.columns:
            application_year = pd.to_datetime(df['issue_d'], errors='coerce').dt.year
        else:
            application_year = pd.Series(pd.Timestamp.now().year, index=df.index)
        return application_year.sub(values.dt.year)
    return pd.Series(0, index=df.index)


def delinquency_flag(df: pd.DataFrame) -> pd.Series:
    if 'delinq_2yrs' in df.columns:
        return (df['delinq_2yrs'] > 0).astype(int)
    return pd.Series(0, index=df.index)


def inquiry_intensity(df: pd.DataFrame) -> pd.Series:
    cols = ['inq_last_6mths', 'inq_last_12m', 'inq_fi']
    present = [c for c in cols if c in df.columns]
    if not present:
        return pd.Series(0, index=df.index)
    return df[present].fillna(0).sum(axis=1)


def utilization_category(df: pd.DataFrame) -> pd.Series:
    if 'revol_util' not in df.columns:
        return pd.Series('unknown', index=df.index)
    value = df['revol_util'].fillna(0)
    return pd.cut(
        value,
        bins=[-0.01, 0.3, 0.6, float('inf')],
        labels=['low', 'moderate', 'high'],
        right=False,
    )


def debt_burden_category(df: pd.DataFrame) -> pd.Series:
    if 'dti' not in df.columns:
        return pd.Series('unknown', index=df.index)
    value = df['dti'].fillna(0)
    return pd.cut(
        value,
        bins=[-0.01, 10, 20, 30, float('inf')],
        labels=['low', 'moderate', 'high', 'very_high'],
        right=False,
    )


def employment_stability(df: pd.DataFrame) -> pd.Series:
    if 'emp_length' not in df.columns:
        return pd.Series('unknown', index=df.index)
    val = pd.to_numeric(df['emp_length'], errors='coerce').fillna(0)
    bins = [-1, 1, 3, 5, 10, float('inf')]
    labels = ['new', 'low', 'moderate', 'stable', 'very_stable']
    return pd.cut(val, bins=bins, labels=labels, right=False)


def income_category(df: pd.DataFrame) -> pd.Series:
    if 'annual_inc' not in df.columns:
        return pd.Series('unknown', index=df.index)
    value = pd.to_numeric(df['annual_inc'], errors='coerce').fillna(0)
    return pd.cut(
        value,
        bins=[-0.01, 30000, 60000, 100000, float('inf')],
        labels=['low', 'moderate', 'high', 'very_high'],
        right=False,
    )


def loan_amount_category(df: pd.DataFrame) -> pd.Series:
    if 'loan_amnt' not in df.columns:
        return pd.Series('unknown', index=df.index)
    value = pd.to_numeric(df['loan_amnt'], errors='coerce').fillna(0)
    return pd.cut(
        value,
        bins=[-0.01, 5000, 15000, 30000, float('inf')],
        labels=['small', 'medium', 'large', 'very_large'],
        right=False,
    )


def build_fintech_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out['loan_to_income_ratio'] = loan_to_income_ratio(out)
    out['average_fico'] = average_fico(out)
    out['credit_history_length'] = credit_history_length(out)
    out['delinquency_flag'] = delinquency_flag(out)
    out['inquiry_intensity'] = inquiry_intensity(out)
    out['utilization_category'] = utilization_category(out)
    out['debt_burden_category'] = debt_burden_category(out)
    out['employment_stability'] = employment_stability(out)
    out['income_category'] = income_category(out)
    out['loan_amount_category'] = loan_amount_category(out)
    return out


def select_model_features(df: pd.DataFrame, target: str = 'default_flag') -> tuple[pd.DataFrame, pd.Series]:
    feature_columns = [
        'loan_amnt', 'annual_inc', 'loan_to_income_ratio', 'average_fico', 'dti',
        'revol_util', 'delinq_2yrs', 'employment_stability', 'utilization_category',
        'debt_burden_category', 'credit_history_length', 'inquiry_intensity',
        'delinquency_flag', 'income_category', 'loan_amount_category'
    ]
    present = [c for c in feature_columns if c in df.columns]
    X = df[present].copy()
    y = df[target]
    return X, y
