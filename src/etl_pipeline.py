from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT_DIR / 'lendingLoan zip' / 'loan.csv'
PROCESSED_DIR = ROOT_DIR / 'data' / 'processed'


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to snake_case and normalize common formatting."""
    renamed = df.copy()
    renamed.columns = [str(c).strip().lower().replace(' ', '_').replace('-', '_') for c in renamed.columns]
    renamed.columns = [c.replace('/', '_').replace('(', '').replace(')', '') for c in renamed.columns]
    return renamed


def build_default_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Create a conservative business-safe default flag from loan_status."""
    out = df.copy()
    default_statuses = {
        'Charged Off',
        'Default',
        'Late (31-120 days)',
        'Late (16-30 days)'
    }
    out['default_flag'] = out['loan_status'].fillna('').isin(default_statuses).astype(int)
    return out


def safe_to_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors='coerce')


def clean_numeric(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors='coerce')
    return out


def normalize_text(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = out[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
    return out


def build_customer_table(df: pd.DataFrame) -> pd.DataFrame:
    customer = df.copy()
    customer['member_id'] = pd.to_numeric(customer['member_id'], errors='coerce')
    missing_mask = customer['member_id'].isna()
    if missing_mask.any():
        customer.loc[missing_mask, 'member_id'] = pd.Series(
            range(1, missing_mask.sum() + 1),
            index=customer.index[missing_mask],
        )
    customer['customer_id'] = customer['member_id']

    # Keep the schema compatible with dataset variants that omit FICO columns.
    for fico_column in ['fico_range_low', 'fico_range_high']:
        if fico_column not in customer.columns:
            customer[fico_column] = float('nan')

    keep = [
        'customer_id', 'member_id', 'addr_state', 'zip_code', 'annual_inc', 'annual_inc_joint',
        'emp_title', 'emp_length', 'home_ownership', 'application_type', 'earliest_cr_line',
        'fico_range_low', 'fico_range_high', 'delinq_2yrs', 'delinq_amnt', 'pub_rec',
        'pub_rec_bankruptcies', 'mort_acc', 'open_acc',
        'total_acc', 'revol_bal', 'revol_util', 'total_bal_ex_mort', 'tot_cur_bal', 'tot_coll_amt',
        'inq_last_6mths', 'inq_last_12m', 'inq_fi', 'acc_now_delinq', 'collections_12_mths_ex_med',
        'chargeoff_within_12_mths'
    ]
    keep = [col for col in keep if col in customer.columns]
    customer = customer[keep].drop_duplicates(subset='member_id').reset_index(drop=True)
    return customer


def build_loan_table(df: pd.DataFrame) -> pd.DataFrame:
    loan = df.copy()
    loan['loan_id'] = pd.to_numeric(loan['id'], errors='coerce')
    missing_loan_ids = loan['loan_id'].isna()
    if missing_loan_ids.any():
        loan.loc[missing_loan_ids, 'loan_id'] = pd.Series(
            range(1, missing_loan_ids.sum() + 1),
            index=loan.index[missing_loan_ids],
        )

    loan['member_id'] = pd.to_numeric(loan['member_id'], errors='coerce')
    missing_member_ids = loan['member_id'].isna()
    if missing_member_ids.any():
        loan.loc[missing_member_ids, 'member_id'] = pd.Series(
            range(1, missing_member_ids.sum() + 1),
            index=loan.index[missing_member_ids],
        )
    loan['customer_id'] = loan['member_id']

    keep = [
        'loan_id', 'customer_id', 'member_id', 'loan_amnt', 'funded_amnt', 'term', 'int_rate',
        'installment', 'grade', 'sub_grade', 'purpose', 'title', 'issue_d', 'loan_status',
        'dti', 'verification_status', 'initial_list_status', 'disbursement_method', 'application_type',
        'default_flag', 'effective_int_rate', 'service_fee_rate', 'review_status', 'review_status_d'
    ]
    keep = [col for col in keep if col in loan.columns]
    enriched = {col: loan[col] for col in keep}
    return pd.DataFrame(enriched)


def clean_raw_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(RAW_CSV, low_memory=False)
    df = standardize_columns(raw)
    df = build_default_flag(df)

    # Date conversion
    for date_col in ['issue_d', 'earliest_cr_line', 'last_pymnt_d', 'last_credit_pull_d', 'review_status_d']:
        if date_col in df.columns:
            df[date_col] = safe_to_datetime(df[date_col])

    # Numeric fields common to all lending datasets
    numeric_cols = [
        'loan_amnt', 'funded_amnt', 'funded_amnt_inv', 'annual_inc', 'annual_inc_joint',
        'dti', 'dti_joint', 'delinq_2yrs', 'revol_bal', 'revol_util', 'total_acc', 'open_acc',
        'tot_cur_bal', 'tot_coll_amt', 'inq_last_12m', 'inq_fi', 'acc_now_delinq',
        'collections_12_mths_ex_med', 'chargeoff_within_12_mths', 'installment', 'int_rate',
        'fico_range_low', 'fico_range_high', 'mort_acc', 'pub_rec', 'pub_rec_bankruptcies',
        'revol_bal_joint', 'max_bal_bc', 'bc_util', 'total_rev_hi_lim', 'total_bc_limit'
    ]
    df = clean_numeric(df, numeric_cols)

    text_cols = ['grade', 'sub_grade', 'home_ownership', 'purpose', 'title', 'addr_state', 'emp_title', 'loan_status']
    df = normalize_text(df, text_cols)

    # Save processed files
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    customer = build_customer_table(df)
    loan = build_loan_table(df)

    customer_path = PROCESSED_DIR / 'customers.csv'
    loan_path = PROCESSED_DIR / 'loans.csv'
    customer.to_csv(customer_path, index=False)
    loan.to_csv(loan_path, index=False)

    return customer, loan


if __name__ == '__main__':
    customer, loan = clean_raw_dataset()
    print('Customer rows:', len(customer))
    print('Loan rows:', len(loan))
    print('Customer columns:', customer.columns.tolist())
    print('Loan columns:', loan.columns.tolist())
