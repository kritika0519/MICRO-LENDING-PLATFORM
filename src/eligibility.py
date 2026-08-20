from __future__ import annotations


def evaluate_eligibility(applicant: dict, loan: dict, risk_score: int = 0, default_probability: float = 0.0) -> dict:
    """Evaluate business eligibility using practical rule checks.

    Important: thresholds are recommendations, not strict PDF requirements.
    """
    reasons = []
    eligible = True

    annual_inc = float(applicant.get('annual_inc', 0) or 0)
    loan_amt = float(loan.get('loan_amnt', 0) or 0)
    dti = float(loan.get('dti', 0) or 0)
    revol_util = float(applicant.get('revol_util', 0) or 0)
    emp_length = float(applicant.get('emp_length', 0) or 0)
    fico = float(applicant.get('fico_range_low', 0) or applicant.get('fico_range_high', 0) or 0)
    delinq_2yrs = int(applicant.get('delinq_2yrs', 0) or 0)
    recent_inq = int(applicant.get('inq_last_6mths', 0) or 0)

    if annual_inc < 20000:
        eligible = False
        reasons.append('Annual income below minimum threshold')

    loan_to_income = (loan_amt / annual_inc) if annual_inc > 0 else 0
    if loan_to_income > 0.45:
        eligible = False
        reasons.append('Loan-to-income ratio exceeds recommended limit')

    if dti > 40:
        eligible = False
        reasons.append('DTI exceeds permissible limit')

    if revol_util > 0.85:
        eligible = False
        reasons.append('Credit utilization too high')

    if emp_length < 1:
        eligible = False
        reasons.append('Employment length is below minimum threshold')

    if fico and fico < 580:
        eligible = False
        reasons.append('FICO is below minimum threshold')

    if delinq_2yrs >= 3:
        eligible = False
        reasons.append('Delinquency history indicates elevated risk')

    if recent_inq >= 6:
        eligible = False
        reasons.append('Recent inquiry intensity is too high for approval')

    if default_probability > 0.30:
        eligible = False
        reasons.append('Default probability exceeds lending tolerance')

    if risk_score >= 75:
        eligible = False
        reasons.append('Risk score is above approval threshold')

    if not reasons:
        reasons.append('Applicant meets the minimum rule-based eligibility checks')

    return {
        'eligible': eligible,
        'loan_to_income_ratio': loan_to_income,
        'reasons': reasons,
    }
